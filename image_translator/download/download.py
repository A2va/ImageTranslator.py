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

import os
from zipfile import ZipFile
from urllib.request import urlretrieve


def printProgressBar(prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    def progress_hook(count, blockSize, totalSize):
        progress = count * blockSize / totalSize
        percent = ("{0:." + str(decimals) + "f}").format(progress * 100)
        filledLength = int(length * progress)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    return progress_hook


def download_and_unzip(url, filename, model_storage_directory, desc, extract_all=False):
    zip_path = os.path.join(model_storage_directory, 'temp.zip')
    progress_bar = printProgressBar(prefix='Progress:', suffix='Complete', length=50)
    urlretrieve(url, zip_path, reporthook=progress_bar)
    with ZipFile(zip_path, 'r') as zipObj:
        if extract_all:
            zipObj.extractall(model_storage_directory)
        else:
            zipObj.extract(filename, model_storage_directory)
    os.remove(zip_path)
