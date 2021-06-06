# Copyright (C) 2020  A2va

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import List, Optional, Union, TypedDict

# Image
import cv2
import numpy as np

import PIL.Image as PIL_Img
import PIL.ImageFont as PIL_ImgFont
import PIL.ImageDraw as PIL_ImgDraw


# OCR
import easyocr
import pytesseract
from image_translator.utils.text_binarization import TextBin
# Translator
from googletrans import Translator
from PyBinglate import BingTranslator
from image_translator.utils.deeplv2 import DeepL
from image_translator.utils import lang

import sys

import urllib.request

# Logging
import logging

logFormatter = logging.Formatter(
    "[%(asctime)s] "
    "[%(levelname)-5.5s]: "
    "%(message)s")
log = logging.getLogger('image_translator')
fileHandler = logging.FileHandler('latest.log')
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

log.setLevel(logging.WARNING)

if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = 'tesseract-ocr/tesseract.exe'

TRANS = {
    'google': 0,
    'bing': 1,
    'deepl': 2
}
OCR = {
    'tesseract': 0,
    'easyocr': 1
}


# Dict type to represent a word or words
class Word(TypedDict):
    x1: int
    y1: int
    x2: int
    y2: int
    w: int
    h: int
    text: str


# Dicty type for paragraph
class Paragraph(TypedDict):
    x: int
    y: int
    w: int
    h: int
    text: str
    image: np.ndarray
    max_width: int
    translated_string: str
    word_list: List[Word]


def convert_tesserract_output(data, x: int, y: int) -> List[Word]:
    word: List[Word] = []
    for item in zip(data['text'], data['left'], data['top'], data['width'], data['height']):
        if item[0] != '':
            x1: int = item[1] + x
            y1: int = item[2] + y
            x2: int = item[3] + x1
            y2: int = item[4] + y1
            word.append({
                'text': item[0],
                'x1': x1 - 6,
                'y1': y1 - 6,
                'x2': x2 + 6,
                'y2': y2 + 6,
                'w': item[3] + 6,
                'h': item[4] + 6
            })
    return word


class UnknownLanguage(Exception):
    pass


class ImageTranslator():
    """
    The image translator class
    """

    def __init__(self, img: Union[PIL_Img.Image, np.ndarray, str], ocr: str,
                 translator: str, src_lang: str, dest_lang: str):
        """
        img: path file, bytes URL, Pillow/OpenCV image and data URI\n
        ocr: 'tesseract' or 'easyocr'\n
        translator: 'google' , 'bing' and  'deepl'\n
        src_lang: source language of image. See code in utils.lang\n
        dest_lang: destination language of image. See code in utils.lang\n
        """
        self.img: np.ndarray = ImageTranslator.reformat_input(img)
        self.img_out: Optional[np.ndarray] = None
        self.img_process: Optional[np.ndarray] = None
        self.text: List[Paragraph] = []
        self.mask_paragraph: Optional[np.ndarray] = None
        self.ocr: str = ocr
        self.translator: str = translator
        self.src_lang: str = src_lang
        self.dest_lang: str = dest_lang

        self.trans_src_lang: str = ''
        self.trans_dest_lang: str = ''

        # Test the language code for ocr and translator
        try:
            self.ocr_lang = lang.OCR_LANG[self.src_lang][OCR[self.ocr]]
        except UnknownLanguage:
            log.error(f'Language {self.ocr} is not available')
            raise UnknownLanguage(f'Language {self.ocr} is not available')
        if self.ocr_lang == 'invalid':
            log.warning(f'The {self.ocr} ocr has no {self.src_lang}.'
                        f'Switch to tesseract')
            self.ocr = 'tesseract'

        try:
            self.trans_src_lang = lang.TRANS_LANG[self.src_lang][TRANS[self.translator]]
            self.trans_dest_lang = lang.TRANS_LANG[self.dest_lang][TRANS[self.translator]]
        except UnknownLanguage:
            log.error(f'Language {self.dest_lang} is not available')
            raise UnknownLanguage(
                f'Language {self.dest_lang} is not available')
        if src_lang == 'invalid' or dest_lang == 'invalid':
            log.warning(f'The {self.translator} ocr has no {self.src_lang}'
                        f'or {self.dest_lang}.Switch to google')
            self.trans_src_lang = lang.TRANS_LANG[self.src_lang][TRANS['google']]
            self.trans_dest_lang = lang.TRANS_LANG[self.dest_lang][TRANS['google']]
            self.translator = 'google'

    def translate(self) -> np.ndarray:
        """Processing of the input image and
        direct translation"""

        if self.img_process is None:
            self.processing()
        self.img_out = self.img_process.copy()
        log.debug('Apply translation to image')
        for i in self.text:
            # Draw a rectangle on the original text
            self.__draw_rectangle(i['word_list'])
            if i['string'] != '':
                self.__apply_translation(i)
        return self.img_out

    def get_text(self) -> List[Paragraph]:
        """Return the text list"""
        return self.text

    def processing(self):
        """Process the input image to detect text
        and pass it to the ocr """

        # Retrieve paragraph mask of the image
        self.img_process = self.img.copy()
        self.mask_paragraph = self.__detect_text(self.img)

        # Split all paragraph into a list
        paragraphs: List[Paragraph] = self.__detect_paragraph()

        # Apply Binarization and ocr
        for paragraph in paragraphs:
            binary = TextBin(paragraph['image'])
            paragraph['image'] = binary.run()
            self.text.append(self.__run_ocr(paragraph))

        # Run translator
        for i in self.text:
            if i['string'] != '':
                # Run the translator
                i['translated_string'] = self.run_translator(
                    i['string'])

    def __draw_rectangle(self, word: List[Word]):

        for item in word:
            cv2.rectangle(self.img_out, (item['x1'], item['y1']), (
                          item['x2'], item['y2']), (255, 255, 255), -1)

    def __detect_text(self, img: np.ndarray) -> np.ndarray:
        """
        Return a mask from the text location
        """
        log.debug('Run CRAFT text detector and create mask')
        blank_image: np.ndarray = np.zeros(
            (img.shape[0], img.shape[1], 3), np.uint8)

        reader = easyocr.Reader(['en'])  # Set lang placeholder
        boxes = reader.detect(img)[0]

        # Draw a white rectangle on each detection
        for box in boxes:
            point1 = (int(box[0]), int(box[2]))
            point2 = (int(box[1]), int(box[3]))
            cv2.rectangle(blank_image, point1, point2, (255, 255, 255), -1)

        return blank_image

    def __detect_paragraph(self) -> List[Paragraph]:
        """
        Detect each paragraph with finding coutour
        of the mask_paragraph
        """
        log.debug('Crop each paragraph')
        paragraph: List = []
        img: np.ndarray = self.img.copy()

        # Find contours
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        dilated = cv2.dilate(cv2.cvtColor(self.mask_paragraph,
                             cv2.COLOR_BGR2GRAY), kernel, iterations=9)
        contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_NONE)

        # Crop the image to get only text
        for contour in contours:

            [x, y, w, h] = cv2.boundingRect(contour)
            cropped: np.ndarray = img[y:y + h, x:x + w]

            cropped = cv2.bitwise_and(
                cropped,
                self.mask_paragraph[y:y + h, x:x + w])

            # Apply binarization
            paragraph.append({
                'image': cropped,
                'x': x,
                'y': y,
                'w': w,
                'h': h
            })
        return paragraph

    def __run_ocr(self, paragraph: Paragraph) -> Paragraph:
        """
        Run the selected OCR
        """

        log.debug(f'Run {self.ocr} ocr')
        if self.ocr == 'easyocr':
            return self.__run_easyocr(paragraph, self.ocr_lang)
        elif self.ocr == 'tesseract':
            return self.__run_tesserract(paragraph, self.ocr_lang)

    def __run_tesserract(self, paragraph: Paragraph, lang_code: str) -> Paragraph:
        """
        Run tesserract ocr
        """
        boxes = pytesseract.image_to_data(
            paragraph['image'], lang=lang_code, output_type=pytesseract.Output.DICT)
        x: int = paragraph['x']
        y: int = paragraph['y']
        words: List[Word] = convert_tesserract_output(boxes, x, y)

        x = words[0]['x1']
        y = words[0]['y1']
        text: str = ''
        for item in words:
            text += item['text']
            text += ' '

        paragraph['x'] = x - 40
        paragraph['y'] = y - 15
        paragraph['word_list'] = words
        paragraph['max_width'] = paragraph['w']
        # Only for Cantarell -> Find a solution for all fonts
        paragraph['font_size'] = int(words[0]['h']*1.1)
        paragraph['text'] = text

        return paragraph

    def __run_easyocr(self, paragraph: Paragraph, lang_code: str) -> Paragraph:
        """
        Run EasyOCR
        """
        reader = easyocr.Reader([lang_code], gpu=False,
                                model_storage_directory='easyocr/model')
        result: List = reader.readtext(paragraph['image'])
        # 1|----------------------------|2
        #  |                            |
        # 4|----------------------------|3
        # [[[x1,y1],[x2,y2][x3,y3],[x4,y4],text],confidence]

        x: int = paragraph['x']
        y: int = paragraph['y']

        words: List[Word] = []
        for item in result:

            point1: tuple = item[0][0]
            point2: tuple = item[0][2]
            x1: int = point1[0] + x
            y1: int = point1[1] + y
            words.append({
                'text': item[1],
                'x1': x1 - 6,
                'y1': y1 - 6,
                'x2': point2[0] + x1 + 6,
                'y2': point2[1] + y1 + 6,
                'w': point2[0] - point1[0] + 6,
                'h': point2[1] - point1[1] + 6
                })

        text: str = ''
        for item in words:
            text += item['text']
            text += ' '

        x = words[0]['x1']
        y = words[0]['y1']

        paragraph['x'] = x - 40
        paragraph['y'] = y - 15
        paragraph['word_list'] = words
        paragraph['max_width'] = paragraph['w']
        # Only for Cantarell -> Find a solution for all fonts
        paragraph['font_size'] = int(words[0]['h']*1.1)
        paragraph['text'] = text

        return paragraph

    @staticmethod
    def reformat_input(image: Union[PIL_Img.Image, np.ndarray, str]) -> np.ndarray:
        """
        Reformat the input image
        """
        if type(image) == str:
            # URL
            if image.startswith('http://') or image.startswith('https://'):
                # Read bytes from url
                image = urllib.request.urlopen(image).read()

            nparr = np.frombuffer(image, np.uint8)              # Bytes
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif type(image) == np.ndarray:                         # OpenCV image
            if len(image.shape) == 2:
                img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif len(image.shape) == 3 and image.shape[2] == 3:
                img = image
            elif len(image.shape) == 3 and image.shape[2] == 4:
                img = image[:, :, :3]
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif isinstance(image, PIL_Img.Image):
            img = np.asarray(image)
        else:
            log.error('Invalid input type. Suppoting format ='
                      'string(file path or url), bytes, numpy array')
        return img

    def __text_wrap(self, text: str, font: PIL_ImgFont.FreeTypeFont, max_width: int) -> List[str]:
        """
        Wrap the into multiple lines
        """
        lines = []
        # If the width of the text is smaller than image width
        # we don't need to split it, just add it to the lines array
        # and return
        if font.getsize(text)[0] <= max_width:
            lines.append(text)
        else:
            # split the line by spaces to get words
            words = text.split(' ')
            i = 0

            while i < len(words):
                line = ''
                while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                    line = line + words[i] + " "
                    i += 1
                if not line:
                    line = words[i]
                    i += 1

                lines.append(line)
        return lines

    def run_translator(self, text: str):
        """
        Run translator between Google, Bing and DeepL
        """

        if self.translator == 'google':
            return self.__run_google(text, self.trans_dest_lang,
                                     self.trans_src_lang)
        elif self.translator == 'bing':
            return self.__run_bing(text, self.trans_dest_lang,
                                   self.trans_src_lang)
        elif self.translator == 'deepl':
            return self.__run_deepl(text, self.trans_dest_lang,
                                    self.trans_src_lang)

    def __run_google(self, text: str, dest_lang: str, src_lang: str):
        """
        Run google translator
        """
        tra = Translator()

        string = tra.translate(text, dest_lang, src_lang).text

        return string

    def __run_bing(self, text: str, dest_lang: str, src_lang: str):
        """
        Run bing translator
        """
        tra = BingTranslator()
        string = tra.translate(text, dest_lang, src_lang)

        return string

    def __run_deepl(self, text: str, dest_lang: str, src_lang: str):
        """
        Run deepl translator
        """
        tra = DeepL(text, dest_lang, src_lang)
        string = tra.translate()

        return string

    def __apply_translation(self, text: Paragraph):
        """
        Apply the translation on img_out
        """
        im_pil = PIL_Img.fromarray(self.img_out)
        draw = PIL_ImgDraw.Draw(im_pil)

        font_file_path = 'font/Cantarell.ttf'

        font = PIL_ImgFont.truetype(
            font_file_path,
            size=text['font_size'],
            encoding="unic")

        lines = self.__text_wrap(
            text['translated_string'],
            font,
            text['max_width'])
        line_height = font.getsize('hg')[1]
        y = text['y']
        for line in lines:
            draw.text((text['x'], y), line, fill=(0, 0, 0), font=font)
            y = y + line_height
        self.img_out = np.asarray(im_pil)
