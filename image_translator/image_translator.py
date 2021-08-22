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

from typing import List, Optional, Union
from image_translator.types import Paragraph

# Image
import cv2
import numpy as np

import PIL.Image as PIL_Img
import PIL.ImageFont as PIL_ImgFont
import PIL.ImageDraw as PIL_ImgDraw


# OCR
from image_translator.ocr import Ocr
import easyocr
from image_translator.utils.text_binarization import TextBin

# Translator
from image_translator.translator import Translator

import urllib.request

# Logging
import logging

logFormatter = logging.Formatter(
    "[%(asctime)s] "
    "[%(levelname)-5.5s]: "
    "%(message)s")
log = logging.getLogger('image_translator')

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
log.addHandler(streamHandler)

log.setLevel(logging.DEBUG)


class ImageTranslator():
    """
    The image translator class
    """

    def __init__(self, img: Union[PIL_Img.Image, np.ndarray, str], ocr: str,
                 translator: str, src_lang: str, dest_lang: str,
                 gpu: bool = False, inpainting: bool = False):
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
        self.ocr = Ocr(ocr, src_lang)
        self.translator = Translator(translator, dest_lang, src_lang)

        self.gpu = gpu

        if inpainting:
            self.remove_text = self.__inpainting
        else:
            self.remove_text = self.__draw_rectangle

    def translate(self) -> np.ndarray:
        """Processing of the input image and
        direct translation"""

        if self.img_process is None:
            self.processing()
        self.img_out = self.img_process.copy()
        log.debug('Apply translation to image')
        for item in self.text:
            self.remove_text(item, self.img_out)
            if item['text'] != '':
                self.__apply_translation(item)
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
            self.text.append(self.ocr.readtext(paragraph))

        # Run translator
        for item in self.text:
            if item['text'] != '':
                # Run the translator
                item = self.translator.translate_paragraph(item)
                self.remove_text(item, self.img_process)

    def __draw_rectangle(self, paragraph: Paragraph, img: np.ndarray):
        pt1 = (paragraph['x'], paragraph['y'])
        pt2 = (paragraph['x'] + paragraph['w'], paragraph['y'] + paragraph['h'])
        cv2.rectangle(self.img_process, pt1, pt2, (255, 255, 255), -1)

    def __inpainting(self, paragraph: Paragraph, img: np.ndarray):
        dx: int = paragraph['dx']
        dy: int = paragraph['dy']
        dw: int = paragraph['dw']
        dh: int = paragraph['dh']

        mask = paragraph['bin_image']

        kernel = np.ones((5, 5), np.uint8)
        temp_img = cv2.dilate(mask, kernel, iterations=1)
        temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)

        cv2.inpaint(img[dy:dy + dh, dx:dx + dw], temp_img, 3, cv2.INPAINT_NS)

    def __detect_text(self, img: np.ndarray) -> np.ndarray:
        """
        Return a mask from the text location
        """
        log.debug('Run CRAFT text detector and create mask')
        blank_image: np.ndarray = np.zeros(
            (img.shape[0], img.shape[1], 3), np.uint8)

        reader = easyocr.Reader(['en'], gpu=self.gpu,  # Set lang placeholder
                                model_storage_directory='easyocr/model')
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
            cropped_mask = self.mask_paragraph[y:y + h, x:x + w]
            cropped: np.ndarray = img[y:y + h, x:x + w]

            cropped = cv2.bitwise_and(
                cropped,
                cropped_mask)

            binary = TextBin(cropped)
            bin_image = binary.run()

            indices = np.where(bin_image == [0])
            coordinates = tuple(zip(indices[0], indices[1]))
            bgr_mask = cv2.cvtColor(np.invert(bin_image), cv2.COLOR_GRAY2BGR)
            self.mask_paragraph[y:y + h, x:x + w] = bgr_mask
            # Reverse the numpy array to get RGB color and not BGR
            # Note: BGR format is the default format for opencv
            text_color = tuple(np.flip(cropped[coordinates[0]]))

            # Apply binarization
            paragraph.append({
                'image': cropped,
                'bin_image': bin_image,
                'text_color': text_color,
                'dx': x,
                'dy': y,
                'dw': w,
                'dh': h
            })
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
            text['translated_text'],
            font,
            text['max_width'])
        line_height = font.getsize('hg')[1]
        y = text['y']
        for line in lines:
            draw.text((text['x'], y), line, fill=text['text_color'][::-1], font=font)
            y = y + line_height
        self.img_out = np.asarray(im_pil)
