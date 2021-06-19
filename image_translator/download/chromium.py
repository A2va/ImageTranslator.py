import pyppeteer.chromium_downloader as chromium
from pathlib import Path
import os


def download_chromium():
    if not os.path.exists('./chromium'):
        Path('./chromium').mkdir(parents=True)
    if not Path(f'./chromium/{chromium.REVISION}/{chromium.windowsArchive}/chrome.exe').exists():
        chromium.extract_zip(chromium.download_zip(chromium.get_url()), f'./chromium/{chromium.REVISION}')


if __name__ == "__main__":
    download_chromium()
