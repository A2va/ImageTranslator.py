
import logging
import numpy as np
from image_translator.utils.lang import OCR_LANG

from image_translator.exceptions import UnknownLanguage, UnknownOCR
OCR = {
    'tesseract': 0,
    'easyocr': 1
}

log = logging.getLogger('image_translator')


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

    def readtext(image: np.ndarray) -> str:
        return ""
