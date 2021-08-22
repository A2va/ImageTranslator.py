import unittest

from image_translator.ocr import OCR
from easyocr.utils import reformat_input

from image_translator.types import Paragraph


class TestTranslator(unittest.TestCase):
    '''Testing translator'''

    def setUp(self):
        '''Set up testing objects'''

        url = "https://i.stack.imgur.com/vrkIj.png"
        self.img = reformat_input(url)
        self.paragraph: Paragraph = {
            'img': self.img,
            'bin_image': self.img
        }

        self.text: str = "I am curious about area-filling text rendering options"

        self.expected_output = [self.text,
                                self.text.lower()]
        self.lang = 'eng'

    def test_tesseract(self):
        '''Test tesseract ocr'''
        ocr = OCR('tesseract', self.lang)
        output = ocr.readtext(self.paragraph)

        self.assertIn(output, self.expected_output)

    def test_easocr(self):
        '''Test easyocr ocr'''
        ocr = OCR('easyocr', self.lang)
        output = ocr.readtext(self.paragraph)

        self.assertIn(output['text'], self.expected_output)


if __name__ == '__main__':
    unittest.main()
