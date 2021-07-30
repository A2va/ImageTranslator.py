import logging
from image_translator.utils.lang import TRANS_LANG
from image_translator.exceptions import UnknownLanguage, UnknownTranslator

from image_translator.types import Paragraph

# Translator
from googletrans import Translator as Google
from image_translator.utils.bing import Bing
from image_translator.utils.deepl import DeepL


TRANS = {
    'google': 0,
    'bing': 1,
    'deepl': 2
}

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

    def translate(self, paragraph: Paragraph) -> Paragraph:
        """
        Run translator between Google, Bing and DeepL
        """
        log.debug('Run translator')
        if self.translator == 'google':
            return self.__run_google(paragraph, self.src_lang,
                                     self.dest_lang)
        elif self.translator == 'bing':
            return self.__run_bing(paragraph, self.src_lang,
                                   self.dest_lang)
        elif self.translator == 'deepl':
            return self.__run_deepl(paragraph, self.src_lang,
                                    self.dest_lang)

    def _run_google(self, paragraph: Paragraph, dest_lang: str, src_lang: str) -> str:
        """
        Run google translator
        """
        tra = Google()

        paragraph['translated_text'] = tra.translate(paragraph['text'], dest_lang, src_lang).text

        return paragraph

    def _run_bing(self, paragraph: Paragraph, dest_lang: str, src_lang: str) -> str:
        """
        Run bing translator
        """
        tra = Bing()
        paragraph['translated_text'] = tra.translate(paragraph['text'], src_lang, dest_lang)

        return paragraph

    def _run_deepl(self, paragraph: Paragraph, dest_lang: str, src_lang: str) -> str:
        """
        Run deepl translator
        """
        tra = DeepL(src_lang, dest_lang)
        paragraph['translated_text'] = tra.translate(paragraph['text'])

        return paragraph
