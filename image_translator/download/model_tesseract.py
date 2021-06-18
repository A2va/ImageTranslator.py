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

# URL: https://github.com/tesseract-ocr/tessdata_best/archive/master.zip

from download import download_and_unzip
import sys
import subprocess


def download_models():

    tesseract_path = 'tesseract-ocr/tessdata'
    if sys.platform.startswith('linux'):
        tesseract_path = subprocess.check_output(['where', 'tesseract'], shell=True).decode('utf-8').join('/tessdata')

    download_and_unzip('https://github.com/tesseract-ocr/tessdata_best/archive/master.zip', None, tesseract_path, True)


if __name__ == "__main__":

    download_models()