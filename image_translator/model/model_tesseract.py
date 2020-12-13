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

#URL: https://github.com/tesseract-ocr/tessdata_best/archive/master.zip

from image_translator.model.download import download_and_unzip

def download_model():
    download_and_unzip('https://github.com/tesseract-ocr/tessdata_best/archive/master.zip',None,'tesseract-ocr/tessdata',True)