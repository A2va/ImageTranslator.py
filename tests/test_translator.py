import unittest

from image_translator.translator import Translator

class TestTranslator(unittest.TestCase):
    '''Testing translator'''

    def setUp(self):
        '''Set up testing objects'''
        self.input = "This is a test"
        self.expected_output = ["Ceci est un test",
                                "Il s'agit d'un test",
                                "C'est un test"]
        self.src_lang = 'eng'
        self.dest_lang = 'fra'

    def test_deepl(self):
        '''Test deepl translator'''
        translator = Translator('deepl', self.dest_lang, self.src_lang)
        output = translator.translate(self.input)

        self.assertIn(output, self.expected_output)

    def test_google(self):
        '''Test google translator'''

        translator = Translator('google', self.dest_lang, self.src_lang)
        output = translator.translate(self.input)

        self.assertIn(output, self.expected_output)

    def test_bing(self):
        '''Test bing translator'''

        translator = Translator('bing', self.dest_lang, self.src_lang)
        output = translator.translate(self.input)

        self.assertIn(output, self.expected_output)


if __name__ == '__main__':
    unittest.main()
