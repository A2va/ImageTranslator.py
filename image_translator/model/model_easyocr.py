# This file is part of ImageTranslator.

# ImageTranslator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ImageTranslator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ImageTranslator. If not, see <https://www.gnu.org/licenses/>.

from easyocr.config import model_url, DETECTOR_FILENAME
from image_translator.model.download import download_and_unzip
import os
def download_models():

    if not os.path.exists('./easyocr'):
        os.makedirs('easyocr/model')

    print('Detector model:')
    download_and_unzip(model_url['detector'][0],DETECTOR_FILENAME,'easyocr/model')

    print('EasyOCR models:')
    print('     Latin:')
    download_and_unzip(model_url['latin.pth'][0],'latin.pth','easyocr/model')

    print('     Chinese:')
    download_and_unzip(model_url['chinese.pth'][0],'chinese.pth','easyocr/model')

    print('     Chinese (simplified):')
    download_and_unzip(model_url['chinese_sim.pth'][0],'chinese_sim.pth','easyocr/model')

    print('     Japanese:')
    download_and_unzip(model_url['japanese.pth'][0],'japanese.pth','easyocr/model')

    print('     Korean:')
    download_and_unzip(model_url['korean.pth'][0],'korean.pth','easyocr/model')

    print('     Thai:')
    download_and_unzip(model_url['thai.pth'][0],'thai.pth','easyocr/model')

    print('     Devanagari:')
    download_and_unzip(model_url['devanagari.pth'][0],'devanagari.pth','easyocr/model')

    print('     Cyrillic:')
    download_and_unzip(model_url['cyrillic.pth'][0],'cyrillic.pth','easyocr/model')

    print('     Arabic:')
    download_and_unzip(model_url['arabic.pth'][0],'arabic.pth','easyocr/model')

    print('     Tamil:')
    download_and_unzip(model_url['tamil.pth'][0],'tamil.pth','easyocr/model')

    print('     Bengali:')
    download_and_unzip(model_url['bengali.pth'][0],'bengali.pth','easyocr/model')

    print('     Telugu:')
    download_and_unzip(model_url['telugu.pth'][0],'telugu.pth','easyocr/model')

    print('     Kannada:')
    download_and_unzip(model_url['kannada.pth'][0],'kannada.pth','easyocr/model')
  

