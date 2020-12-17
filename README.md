# ImageTranslator
 
Python 3.8

List of packages:
* [OpenCV](https://github.com/skvark/opencv-python)
* [Pillow](https://github.com/python-pillow/Pillow)
* [Craft text detector](https://github.com/fcakyon/craft-text-detector)
* [Googletrans](https://github.com/ssut/py-googletrans)
* [Pytesseract](https://github.com/madmaze/pytesseract)
* [EasyOCR](https://github.com/JaidedAI/EasyOCR)

The text binarization comes from this [repository](https://github.com/jasonlfunk/ocr-text-extraction) and the algorithm comes from this [paper](http://www.m.cs.osakafu-u.ac.jp/cbdar2007/proceedings/papers/O1-1.pdf).

## Usage

```python
#translator=ImageTranslator(img, ocr, translator, src_lang, dest_lang)
#img: OpenCV image, PIL image, URL
#ocr: 'tesseract' or 'easyOCR'
#translator:'google', 'bing' or 'deepl'
#src_lang and dest_lang: looking the file lang.py
translator=ImageTranslator('https://i.stack.imgur.com/vrkIj.png','tesseract','google','eng','fra')
#For only processing the image
translator.processing()
#For translate the image
translator.translate()
image_out=translator.img_out
#img_out is OpenCV image
#You can use method run_translator for translate string
```
## Installation

### Windows
1. Install the package
```
pip git+git://github.com/A2va/ImageTranslator@master#egg=image_translator
pip install torch==1.7.0+cpu torchvision==0.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
```
2. Download the 4.1.0 version of [tesseract](https://digi.bib.uni-mannheim.de/tesseract/)
3. Extract the files into executable (ex: 7-Zip)
4. Place the extracted files into the *tesseract-ocr* folder at the root of package
5. Download models from EasyOCR and Tesseract with this command `python -m image_translator.download_model -m all`.
The m flag accept three value (all,tesseract,easyocr). The downloading time can be long.


### Linux
1. Install the package
```
pip git+git://github.com/A2va/ImageTranslator@master#egg=image_translator
pip install torch torchvision
```
2. Install tesseract `apt-get install tesseract-ocr`
3. Download models from EasyOCR and Tesseract with this command `python -m image_translator.download_model -m all`.
The m flag accept three value (all,tesseract,easyocr). The downloading time can be long.

## Development

### Windows
1. Clone the repositoy
```
git clone https://github.com/A2va/ImageTranslator.git
pip install -r requirements.txt
pip install torch==1.7.0+cpu torchvision==0.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
```
2. Download the 4.1.0 version of [tesseract](https://digi.bib.uni-mannheim.de/tesseract/)
3. Extract the files into executable (ex: 7-Zip)
4. Place the extracted files into the *tesseract-ocr* folder at the root of package
5. Download models from EasyOCR and Tesseract with this command `python download_model -m all`.
The m flag accept three value (all,tesseract,easyocr). The downloading time can be long.

### Linux
1. Clone the repositoy
```
git clone https://github.com/A2va/ImageTranslator.git
pip install -r requirements.txt
pip install torch torchvision
```
2. Install tesseract `apt-get install tesseract-ocr`
3. Download models from EasyOCR and Tesseract with this command `python download_model -m all`.
The m flag accept three value (all,tesseract,easyocr). The downloading time can be long.