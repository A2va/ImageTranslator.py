
import logging
import sys
# Typings
from typing import List
from image_translator.types import Paragraph, Word
# Exceptions
from image_translator.exceptions import UnknownLanguage, UnknownOCR

# OCR
import easyocr
import pytesseract

from image_translator.utils.lang import OCR_LANG

if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = 'tesseract-ocr/tesseract.exe'

OCR = {
    'tesseract': 0,
    'easyocr': 1
}

log = logging.getLogger('image_translator')


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


class OCR():
    def __init__(self, ocr: str, lang: str):

        # Check if ocr and language are available
        if ocr not in list(OCR.keys()):
            raise UnknownOCR(f'OCR {ocr} is not available')
        if lang not in list(OCR_LANG.keys()):
            raise UnknownLanguage(f'Language {lang} is not available')

        self.ocr: str = ocr
        # Find the code for the selected ocr
        self.ocr_lang: str = OCR_LANG[lang][OCR[self.ocr]]

        # The language is not available fot this ocr
        # Switch to another -> tesseract
        if self.ocr_lang == 'invalid':
            log.warning(f'The {self.ocr} ocr has no {self.src_lang}.'
                        f'Switch to tesseract')
            self.ocr = 'tesseract'
            self.ocr_lang = OCR_LANG[lang][OCR[self.ocr]]

    def readtext(self, paragraph: Paragraph) -> Paragraph:
        """
        Run the selected OCR
        """

        log.debug(f'Run {self.ocr} ocr')
        if self.ocr == 'easyocr':
            return self.__run_easyocr(paragraph, self.ocr_lang)
        elif self.ocr == 'tesseract':
            return self.__run_tesserract(paragraph, self.ocr_lang)

    def _run_tesserract(self, paragraph: Paragraph, lang_code: str) -> Paragraph:
        """
        Run tesserract ocr
        """
        boxes = pytesseract.image_to_data(
            paragraph['bin_image'], lang=lang_code, output_type=pytesseract.Output.DICT)
        dx: int = paragraph['dx']
        dy: int = paragraph['dy']
        words: List[Word] = convert_tesserract_output(boxes, dx, dy)

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

    def _run_easyocr(self, paragraph: Paragraph, lang_code: str) -> Paragraph:
        """
        Run EasyOCR
        """
        reader = easyocr.Reader([lang_code], gpu=self.gpu,
                                model_storage_directory='easyocr/model')
        result: List = reader.readtext(paragraph['bin_image'])
        # 1|----------------------------|2
        #  |                            |
        # 4|----------------------------|3
        # [[[x1,y1],[x2,y2][x3,y3],[x4,y4],text],confidence]

        dx: int = paragraph['dx']
        dy: int = paragraph['dy']

        words: List[Word] = []
        for item in result:

            point1: tuple = item[0][0]
            point2: tuple = item[0][2]
            x1: int = point1[0] + dx
            y1: int = point1[1] + dy
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
