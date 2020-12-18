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

# from easyocr.config import model_url, DETECTOR_FILENAME
model_url = {
    'detector': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip', '2f8227d2def4037cdb3b34389dcf9ec1'),
    'latin.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/latin.zip', 'fb91b9abf65aeeac95a172291b4a6176'),
    'chinese.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/chinese.zip', 'dfba8e364cd98ed4fed7ad54d71e3965'),
    'chinese_sim.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/chinese_sim.zip', '0e19a9d5902572e5237b04ee29bdb636'),
    'japanese.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/japanese.zip', '6d891a4aad9cb7f492809515e4e9fd2e'),
    'korean.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/korean.zip', '45b3300e0f04ce4d03dda9913b20c336'),
    'thai.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/thai.zip', '40a06b563a2b3d7897e2d19df20dc709'),
    'devanagari.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/devanagari.zip', 'db6b1f074fae3070f561675db908ac08'),
    'cyrillic.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/cyrillic.zip', '5a046f7be2a4f7da6ed50740f487efa8'),
    'arabic.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/arabic.zip', '993074555550e4e06a6077d55ff0449a'),
    'tamil.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/v1.1.7/tamil.zip', '4b93972fdacdcdabe6d57097025d4dc2'),
    'bengali.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/v1.1.8/bengali.zip', 'cea9e897e2c0576b62cbb1554997ce1c'),
    'telugu.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/v1.2/telugu.zip', 'f7576012a3abe593950c47bfa1bd8ddc'),
    'kannada.pth': ('https://github.com/JaidedAI/EasyOCR/releases/download/v1.21/kannada.zip', 'c240c97e4adb8773b53b3b3dec728627'),
}

DETECTOR_FILENAME = 'craft_mlt_25k.pth'

from image_translator.model.download import download_and_unzip
import os
def download_models():

    if not os.path.exists('./easyocr'):
        os.makedirs('easyocr/model')

    if not os.path.exists(f'./easyocr/model/{DETECTOR_FILENAME}'):
        print('Detector model:\n')
        download_and_unzip(model_url['detector'][0],DETECTOR_FILENAME,'easyocr/model')
    
    print('EasyOCR models:\n')
    for name in model_url:
        if not os.path.exists(f'easyocr/model/{name}') and name!='detector':
            download_and_unzip(model_url[name][0],name,'easyocr/model')
    
