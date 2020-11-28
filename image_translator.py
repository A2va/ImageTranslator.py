from __future__ import absolute_import
# Image
import cv2
import numpy as np

import PIL.Image as PIL_Img
import PIL.ImageGrab as PIL_ImgGrab
import PIL.ImageFont as PIL_ImgFont
import PIL.ImageDraw as PIL_ImgDraw

# Text detector
import craft_text_detector as craft_detector

#OCR
import easyocr
import pytesseract
from .utils.text_binarization import TextBin
# Translator
from googletrans import Translator
from PyBinglate import BingTranslator
from .utils.deeplv2 import DeepL
from .utils import lang


import urllib

# Logging
import sys
import logging

logFormatter = logging.Formatter(
    "[%(asctime)s] "
    "[%(levelname)-5.5s]: "
    "%(message)s")
log = logging.getLogger('image_translator')
fileHandler = logging.FileHandler('latest.log')
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

log.setLevel(logging.DEBUG)

pytesseract.pytesseract.tesseract_cmd = 'tesseract-ocr/tesseract.exe'

TRANS = {
    'google': 0,
    'bing': 1,
    'deepl': 2
}
OCR = {
    'tesseract': 0,
    'easyOCR': 1
}

class UnknownLanguage(Exception):
    pass

class ImageTranslator():
    """
    The image translator class
    """
    def __init__(self, img, ocr, translator, src_lang, dest_lang):
        """
        img: path file, bytes URL, Pillow/OpenCV image and data URI\n
        ocr: 'tesseract' or 'easyocr'\n
        translator: 'google' , 'bing' and  'deepl'\n
        src_lang: source language of image. See code in utils.lang\n
        dest_lang: destination language of image. See code in utils.lang\n
        """
        self.img = self.__reformat_input(img)
        self.img_out = None
        self.text = []
        self.mask_paragraph = None
        self.ocr = ocr
        self.translator = translator
        self.src_lang = src_lang
        self.dest_lang = dest_lang

    def translate(self):
        if self.img_out is None:
            self.processing()
        log.debug('Apply translation to image')
        for i in range(0, len(self.text)):
            if self.text[i]['string'] != '':
                self.__apply_translation(self.text[i])
        return self.img_out

    def get_text(self):
        return self.text

    def processing(self):
        self.img_out=self.img.copy()
        self.mask_paragraph = self.__detect_text(self.img)
        paragraphs = self.__detect_paragraph()
        # Apply Binarization and ocr
        for paragraph in paragraphs:
            binary = TextBin(paragraph['image'])
            paragraph['image'] = binary.run()

            self.text.append(self.__run_ocr(paragraph))
        for i in range(0, len(self.text)):
            x = self.text[i]['x']
            y = self.text[i]['y']
            w = self.text[i]['paragraph_w']
            h = self.text[i]['paragraph_h']
            if self.text[i]['string'] != '':
                cv2.rectangle(self.img_out, (x, y), (x+w, y+h), (255, 255, 255), -1)
                self.text[i]['translated_string'] = self.run_translator(self.text[i]['string'])
                
    def __detect_text(self, img):
        """
        Return a mask from the text location
        """
        log.debug('Run CRAFT text detector and create mask')
        blank_image = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
        prediction_result = self.__craft(img)
        boxes = prediction_result['boxes']

        for box in boxes:
            point1 = tuple(box[0])
            point2 = tuple(box[2])
            cv2.rectangle(blank_image, point1, point2, (255, 255, 255), -1)

        return blank_image

    def __detect_paragraph(self):
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
        paragraph = []
        img = self.img.copy()

        # Find contours
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        dilated = cv2.dilate(cv2.cvtColor(self.mask_paragraph,
                             cv2.COLOR_BGR2GRAY), kernel, iterations=9)
        contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_NONE)

        for contour in contours:

            [x, y, w, h] = cv2.boundingRect(contour)
            cropped = img[y:y + h, x:x + w]

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

    def __run_ocr(self, paragraph):
        """
        Run the selected OCR
        """
        try:
            lang_code = lang.OCR_LANG[self.src_lang][OCR[self.ocr]]
        except:
            log.error(f'Language {self.ocr} is not available')
            raise UnknownLanguage(f'Language {self.ocr} is not available')
        if lang_code == 'invalid':
            log.warning(f'The {self.ocr} ocr has no {self.src_lang}.'
                        f'Switch to tesseract')
            lang_code = lang.OCR_LANG[self.src_lang][OCR['tesseract']]
            return self.__run_tesserract(paragraph, lang_code)
            
        log.debug(f'Run {self.ocr} ocr')
        if self.ocr == 'easyocr':
            return self.__run_easyocr(paragraph, lang_code)
        elif self.ocr == 'tesseract':
            return self.__run_tesserract(paragraph, lang_code)

    def __run_tesserract(self, paragraph, lang_code):
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
        first = True
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
                'font_zize': int(h*1.1)      #Only for Cantarell -> Find a solution for all fonts
                }

    def __run_easyocr(self, paragraph,lang_code):
        """
        Run EasyOCR
        """
        reader = easyocr.Reader([lang_code])
        result = reader.readtext(paragraph['image'])
        # 1|----------------------------|2
        #  |                            |
        # 4|----------------------------|3
        # [[[x1,y1],[x2,y2][x3,y3],[x4,y4],text],confidence]
        x = result[0][0][0][0]
        y = result[0][0][0][1]
        w = result[0][0][2][0] - x
        h = result[0][0][2][1] - y
        string = ''
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
                'font_zize': int(h*1.1)      #Only for Cantarell -> Find a solution for all fonts
            }

    def __craft(self, img):
        """
        Return a predication of text location
        """
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if img.shape[0] == 2:
            img = img[0]
        if img.shape[2] == 4:
            img = img[:, :, :3]

        refine_net = craft_detector.load_refinenet_model(cuda=False)
        craft_net = craft_detector.load_craftnet_model(cuda=False)
        prediction_result = craft_detector.get_prediction(
            image=img,
            craft_net=craft_net, refine_net=refine_net, text_threshold=0.7,
            link_threshold=0.4, low_text=0.4, cuda=False, long_size=1280)

        return prediction_result

    def __reformat_input(self, image):
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

    def __text_wrap(self, text, font, max_width):
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

    def run_translator(self, text):
        """
        Run translator between Google, Bing and DeepL
        """
        log.debug(f'Run {self.translator} translator')
        try:
            src_lang = lang.TRANS_LANG[self.src_lang][TRANS[self.translator]]
            dest_lang = lang.TRANS_LANG[self.dest_lang][TRANS[self.translator]]
        except:
            log.error(f'Language {self.dest_lang} is not available')
            raise UnknownLanguage(f'Language {self.dest_lang} is not available')
        if src_lang == 'invalid' or dest_lang == 'invalid':
            log.warning(f'The {self.translator} ocr has no {self.src_lang}'
                        f'or {self.dest_lang}.Switch to google')
            src_lang = lang.TRANS_LANG[self.src_lang][TRANS['google']]
            dest_lang = lang.TRANS_LANG[self.dest_lang][TRANS['google']]

            return self.__run_google(text, dest_lang, src_lang)

        if self.translator == 'google':
            return self.__run_google(text, dest_lang, src_lang)
        elif self.translator == 'bing':
            return self.__run_bing(text, dest_lang, src_lang)
        elif self.translator == 'deepl':
            return self.__run_deepl(text, dest_lang, src_lang)

    def __run_google(self, text, dest_lang, src_lang):
        """
        Run google translator
        """
        tra = Translator()

        string = tra.translate(text, dest_lang, src_lang).text

        return string

    def __run_bing(self, text, dest_lang, src_lang):
        """
        Run bing translator
        """
        tra = BingTranslator()
        string = tra.translate(text, dest_lang, src_lang)

        return string

    def __run_deepl(self, text, dest_lang, src_lang):
        """
        Run deepl translator
        """
        tra = DeepL(text, dest_lang, src_lang)
        string = tra.translate()

        return string

    def __apply_translation(self, text):
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
