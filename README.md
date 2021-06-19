# ImageTranslator
 
This is a image translator package for python. This package is used by this [project](https://github.com/a2va/transimage)

The text binarization comes from this [repository](https://github.com/jasonlfunk/ocr-text-extraction) and the algorithm comes from this [paper](http://www.m.cs.osakafu-u.ac.jp/cbdar2007/proceedings/papers/O1-1.pdf).

**At the moment the Bing translator will not work**

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

```
python -m pip install torch==1.7.0+cpu torchvision==0.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
python -m pip install easyocr
```
If you want to develop use git clone instead of pip installation
```
python -m pip git+git://github.com/A2va/ImageTranslator
```

Use get-components command to download additionnal components.
```
get-components --mode all
```
You can replace all mode by one them:
* tesseract : Download [tessdata_best](https://github.com/tesseract-ocr/tessdata_best), store it in the tesseract path. 
* easyocr: Download all easyocr models
* pyppeteer: Download chromium for using pyppeteer