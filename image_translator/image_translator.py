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

# Text detector
import craft_text_detector as craft_detector
import craft_text_detector.torch_utils as torch_utils
from collections import OrderedDict
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


class Paragraph(TypedDict):
    x: int
    y: int
    w: int
    h: int
    paragraph_w: int
    paragraph_h: int
    string: str
    image: np.ndarray
    max_width: int
    translated_string: str


def copyStateDict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        start_idx = 1
    else:
        start_idx = 0
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = ".".join(k.split(".")[start_idx:])
        new_state_dict[name] = v
    return new_state_dict


def load_craftnet_model(cuda: bool = False):

    from craft_text_detector.models.craftnet import CraftNet

    craft_net = CraftNet()  # initialize
    weight_path = 'easyocr/model/craft_mlt_25k.pth'

    # arange device
    if cuda:
        craft_net.load_state_dict(copyStateDict(torch_utils.load(weight_path)))

        craft_net = craft_net.cuda()
        craft_net = torch_utils.DataParallel(craft_net)
        torch_utils.cudnn_benchmark = False
    else:
        craft_net.load_state_dict(
            copyStateDict(torch_utils.load(weight_path, map_location="cpu"))
        )
    craft_net.eval()
    return craft_net


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
        if self.img_process is None:
            self.processing()
        self.img_out = self.img_process.copy()
        log.debug('Apply translation to image')
        for i in range(0, len(self.text)):
            if self.text[i]['string'] != '':
                self.__apply_translation(self.text[i])
        return self.img_out

    def get_text(self) -> List:
        return self.text

    def processing(self):
        self.img_process = self.img.copy()
        self.mask_paragraph = self.__detect_text(self.img)
        paragraphs: List[Paragraph] = self.__detect_paragraph()
        # Apply Binarization and ocr
        for paragraph in paragraphs:
            binary = TextBin(paragraph['image'])
            paragraph['image'] = binary.run()

            self.text.append(self.__run_ocr(paragraph))
        for i in range(0, len(self.text)):
            x: int = self.text[i]['x']
            y: int = self.text[i]['y']
            w: int = self.text[i]['paragraph_w']
            h: int = self.text[i]['paragraph_h']
            if self.text[i]['string'] != '':
                cv2.rectangle(self.img_process, (x, y),
                              (x+w, y+h), (255, 255, 255), -1)
                self.text[i]['translated_string'] = self.run_translator(
                    self.text[i]['string'])

    def __detect_text(self, img: np.ndarray) -> np.ndarray:
        """
        Return a mask from the text location
        """
        log.debug('Run CRAFT text detector and create mask')
        blank_image: np.ndarray = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
        prediction_result = self.__craft(img)
        boxes = prediction_result['boxes']

        for box in boxes:
            point1 = tuple(box[0])
            point2 = tuple(box[2])
            cv2.rectangle(blank_image, point1, point2, (255, 255, 255), -1)

        return blank_image

    def __detect_paragraph(self) -> List[Paragraph]:
        """
        Return a dict {
             'image':cropped,
             'x':x,
             'y':y,
             'w':w,
             'h':h
        }
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
            Return a dict
            {
                'x':x,
                'y':y,
                'w':w,
                'h':h,
                'paragraph_w':paragepah width,
                'paragraph_h':paragraph height,
                'string':string,
                'image': image,
                'max_width':max width of paragraph
            }
        """
        boxes = pytesseract.image_to_data(paragraph['image'], lang=lang_code)
        string = ''
        x, y, w, h = (0, 0, 0, 0)
        first: bool = True
        for a, b in enumerate(boxes.splitlines()):
            if a != 0:
                b = b.split()
                if len(b) == 12:
                    if first:
                        x = int(b[6])
                        y = int(b[7])
                        w = int(b[8])
                        h = int(b[9])
                        first = False
                    string = string + str(b[11])+' '
        return {
            'x': x + paragraph['x'] - 40,
            'y': y + paragraph['y'] - 15,
            'w': w,
            'h': h,
            'paragraph_w': paragraph['w'] + 20,
            'paragraph_h': paragraph['h'] + 20,
            'string': string,
            'image': paragraph['image'],
            'max_width': paragraph['w'],
            # Only for Cantarell -> Find a solution for all fonts
            'font_size': int(h*1.1)
        }

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
        x: int = result[0][0][0][0]
        y: int = result[0][0][0][1]
        w: int = result[0][0][2][0] - x
        h: int = result[0][0][2][1] - y
        string: str = ''
        for res in result:
            string += res[1]
        return {
            'x': x + paragraph['x'] - 40,
            'y': y + paragraph['y'] - 15,
            'w': w,
            'h': h,
            'paragraph_w': paragraph['w'] + 20,
            'paragraph_h': paragraph['h'] + 20,
            'string': string,
            'image':  paragraph['image'],
            'max_width': paragraph['w'],
            # Only for Cantarell -> Find a solution for all fonts
            'font_size': int(h*1.1)
        }

    def __craft(self, img: np.ndarray):
        """
        Return a predication of text location
        """
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if img.shape[0] == 2:
            img = img[0]
        if img.shape[2] == 4:
            img = img[:, :, :3]

        craft_net = load_craftnet_model(cuda=False)
        prediction_result = craft_detector.get_prediction(
            image=img,
            craft_net=craft_net, refine_net=None, text_threshold=0.7,
            link_threshold=0.4, low_text=0.4, cuda=False, long_size=1280)

        return prediction_result

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

    def __text_wrap(self, text: str, font: PIL_ImgFont.FreeTypeFont, max_width: int) -> List:
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
