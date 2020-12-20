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

from tqdm import tqdm


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_and_unzip(url, filename, model_storage_directory,desc,extract_all=False):
    zip_path = os.path.join(model_storage_directory, 'temp.zip')
    progress_bar=DownloadProgressBar(unit='B', unit_scale=True,miniters=1, desc=desc)
    urlretrieve(url, zip_path,reporthook=progress_bar.update_to)
    with ZipFile(zip_path, 'r') as zipObj:
        if extract_all:
            zipObj.extractall(model_storage_directory)
        else:
            zipObj.extract(filename, model_storage_directory)
    os.remove(zip_path)