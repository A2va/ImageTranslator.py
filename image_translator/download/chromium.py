import pyppeteer.chromium_downloader as chromium
from pathlib import Path
import os
import sys

# Logging
import logging
log = logging.getLogger('image_translator')


def download_chromium():

    if sys.platform.startswith('linux'):
        log.warn('Linux download are not supported. Install chrome or chromium.')
        return

    if not os.path.exists('./chromium'):
        Path('./chromium').mkdir(parents=True)
    if not Path(f'./chromium/{chromium.REVISION}/{chromium.windowsArchive}/chrome.exe').exists():
        chromium.extract_zip(chromium.download_zip(chromium.get_url()), f'./chromium/{chromium.REVISION}')


if __name__ == "__main__":
    download_chromium()
