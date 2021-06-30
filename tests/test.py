import unittest

from googletrans import Translator as Google
from image_translator.utils.deeplv2 import DeepL


class TestTranslator(unittest.TestCase):
    '''Testing translator'''

    def setUp(self):
        '''Set up testing objects'''
        self.text = "This is a test"
        self.src_lang = 'en'
        self.dest_lang = 'fr'

    def test_deepl(self):
        '''Test deepl translator'''

        translator = DeepL(self.src_lang, self.dest_lang)

        self.assertEqual(translator.translate(self.text), 'Ceci est un test')

    def test_google(self):
        '''Test google translator'''

        translator = Google()

        self.assertEqual(translator.translate(self.text, self.src_lang, self.dest_lang), 'Ceci est un test')


if __name__ == '__main__':
    unittest.main()