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

from easyocr.config import recognition_models, detection_models
from image_translator.download.download import download_and_unzip
import os


def download_models():

    if not os.path.exists('./easyocr'):
        os.makedirs('easyocr/model')

    detector_filename = detection_models['craft']['filename']
    if not os.path.exists(f'./easyocr/model/{detector_filename}'):
        print('Detector model:\n')
        download_and_unzip(
            detection_models['craft']['url'], detector_filename, 'easyocr/model', detector_filename)

    print('EasyOCR models:')
    print('Gen1')
    for model in recognition_models['gen1']:
        url = recognition_models['gen1'][model]['url']
        filename = recognition_models['gen1'][model]['filename']
        if not os.path.exists(f'easyocr/model/{filename}'):
            download_and_unzip(url, filename, 'easyocr/model', filename)

    print('Gen2')
    for model in recognition_models['gen2']:
        url = recognition_models['gen2'][model]['url']
        filename = recognition_models['gen2'][model]['filename']
        if not os.path.exists(f'easyocr/model/{filename}'):
            download_and_unzip(url, filename, 'easyocr/model', filename)


if __name__ == '__main__':
    download_models()
