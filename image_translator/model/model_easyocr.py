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

    os.makedirs('easyocr/model')

    print('Detector model:')
    download_and_unzip(model_url['detector'],DETECTOR_FILENAME,'easyocr/model')

    print('EasyOCR models:')
    print('     Latin:')
    download_and_unzip(model_url['latin.pth'],'latin.pth','easyocr/model')

    print('     Chinese:')
    download_and_unzip(model_url['chinese.pth'],'chinese.pth','easyocr/model')

    print('     Chinese (simplified):')
    download_and_unzip(model_url['chinese_sim.pth'],'chinese_sim.pth','easyocr/model')

    print('     Japanese:')
    download_and_unzip(model_url['japanese.pth'],'japanese.pth','easyocr/model')

    print('     Korean:')
    download_and_unzip(model_url['korean.pth'],'korean.pth','easyocr/model')

    print('     Thai:')
    download_and_unzip(model_url['thai.pth'],'thai.pth','easyocr/model')

    print('     Devanagari:')
    download_and_unzip(model_url['devanagari.pth'],'devanagari.pth','easyocr/model')

    print('     Cyrillic:')
    download_and_unzip(model_url['cyrillic.pth'],'cyrillic.pth','easyocr/model')

    print('     Arabic:')
    download_and_unzip(model_url['arabic.pth'],'arabic.pth','easyocr/model')

    print('     Tamil:')
    download_and_unzip(model_url['tamil.pth'],'tamil.pth','easyocr/model')

    print('     Bengali:')
    download_and_unzip(model_url['bengali.pth'],'bengali.pth','easyocr/model')

    print('     Telugu:')
    download_and_unzip(model_url['telugu.pth'],'telugu.pth','easyocr/model')

    print('     Kannada:')
    download_and_unzip(model_url['kannada.pth'],'kannada.pth','easyocr/model')
  

