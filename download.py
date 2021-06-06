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

import image_translator.download.model_easyocr as easyocr
import image_translator.download.model_tesseract as tesseract
import image_translator.download.chromium as pyppeteer
import getopt
import sys

short_options = "m:"
long_options = ["mode="]

if __name__ == "__main__":

    args = sys.argv
    args = args[1:]

    try:
        arguments, values = getopt.getopt(args, short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    for arg, value in arguments:
        if arg in ("-m", "--mode"):
            if value == 'tesseract':
                tesseract.download_models()
            elif value == 'easyocr':
                easyocr.download_models()
            elif value == 'pyppeteer':
                pyppeteer.download_chromium()
            elif value == 'all':
                print('Download all models')
                easyocr.download_models()
                tesseract.download_models()
            else:
                print("Error: Wrong argument value")
        else:
            print("Error: Wrong argument")
