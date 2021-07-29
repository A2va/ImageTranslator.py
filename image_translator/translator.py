import logging
from image_translator.utils.lang import TRANS_LANG

TRANS = {
    'google': 0,
    'bing': 1,
    'deepl': 2
}


class UnknownTranslator(Exception):
    pass


class UnknownLanguage(Exception):
    pass


log = logging.getLogger('image_translator')


class Translator():
    def __init__(self, translator: str, src_lang: str, dest_lang: str):

        # Check if ocr and language are available
        if translator not in list(TRANS.keys()):
            raise UnknownTranslator(f'Translator {translator} is not available')
        if src_lang not in list(TRANS_LANG.keys()):
            raise UnknownLanguage(f'Language {src_lang} is not available')
        if dest_lang not in list(TRANS_LANG.keys()):
            raise UnknownLanguage(f'Language {dest_lang} is not available')

        self.translator: str = translator
        # Find the code for the selected translator
        self.src_lang: str = TRANS_LANG[src_lang][TRANS[self.translator]]
        self.dest_lang: str = TRANS_LANG[dest_lang][TRANS[self.translator]]

        # The language is not available fot this ocr
        # Switch to another -> tesseract
        if src_lang == 'invalid' or dest_lang == 'invalid':
            log.warning(f'The {self.translator} translator has no {self.src_lang}.'
                        f'or {self-dest_lang}'
                        f'Switch to google')
            self.translator = 'google'
            self.src_lang = TRANS_LANG[src_lang][TRANS[self.ocr]]
            self.dest_lang = TRANS_LANG[dest_lang][TRANS[self.ocr]]

    def translate(text: str) -> str:
        return ""
