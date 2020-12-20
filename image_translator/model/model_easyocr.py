# Copyright (C) 2020  A2va

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from easyocr.config import model_url, DETECTOR_FILENAME
from image_translator.model.download import download_and_unzip
import os

def download_models():

    if not os.path.exists('./easyocr'):
        os.makedirs('easyocr/model')

    if not os.path.exists(f'./easyocr/model/{DETECTOR_FILENAME}'):
        print('Detector model:\n')
        download_and_unzip(model_url['detector'][0],DETECTOR_FILENAME,'easyocr/model',DETECTOR_FILENAME)
    
    print('EasyOCR models:\n')
    for name in model_url:
        if not os.path.exists(f'easyocr/model/{name}') and name!='detector':
            download_and_unzip(model_url[name][0],name,'easyocr/model',name)

