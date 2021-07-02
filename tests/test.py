import unittest

from googletrans import Translator as Google
from image_translator.utils.deeplv2 import DeepL


class TestTranslator(unittest.TestCase):
    '''Testing translator'''

    def setUp(self):
        '''Set up testing objects'''
        self.input = "This is a test"
        self.expected_output = ["Ceci est un test", "Il s'agit d'un test"]
        self.src_lang = 'en'
        self.dest_lang = 'fr'

    def test_deepl(self):
        '''Test deepl translator'''

        translator = DeepL(self.src_lang, self.dest_lang)
        output = translator.translate(self.input)

        self.assertIn(output, self.expected_output)

    def test_google(self):
        '''Test google translator'''

        translator = Google()
        output = translator.translate(self.input, self.src_lang, self.dest_lang)

        self.assertIn(output, self.expected_output)  


if __name__ == '__main__':
    unittest.main()
