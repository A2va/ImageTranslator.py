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

### Windows
1. Install the package
```
python -m pip install torch==1.7.0+cpu torchvision==0.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
python -m pip install easyocr
python -m pip install craft-text-detector
python -m pip git+git://github.com/A2va/ImageTranslator@master#egg=ImageTranslator
```
2. Download the 4.1.0 version of [tesseract](https://digi.bib.uni-mannheim.de/tesseract/)
3. Extract the files into executable (ex: 7-Zip)
4. Place the extracted files into the *tesseract-ocr* folder at the root of package
5. Download [tessdata](https://github.com/tesseract-ocr/tessdata) or [tessdata_best](https://github.com/tesseract-ocr/tessdata_best)
6. Place the traineddata files into the tessdata folder.
7. Download models from EasyOCR `python -m image_translator.download_model`.
*Note: Sometimes the progress bar stop so put a character on terminal*

### Linux
1. Install the package
```
python -m pip install easyocr
python -m pip install craft-text-detector
python -m pip git+git://github.com/A2va/ImageTranslator@master#egg=ImageTranslator
```
2. Install tesseract (v4.1.0)
3. Download [tessdata](https://github.com/tesseract-ocr/tessdata) or [tessdata_best](https://github.com/tesseract-ocr/tessdata_best)
4. Place the traineddata files into the tessdata folder ('whereis tesseract').
5. Download models from EasyOCR `python -m image_translator.download_model`.
*Note: Sometimes the progress bar stop so put a character on terminal*

## Development

### Windows
1. Clone the repositoy
```
git clone https://github.com/A2va/ImageTranslator.git
python -m pip install torch==1.7.0+cpu torchvision==0.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
python -m pip install easyocr
python -m pip install craft-text-detector
python -m pip install -r requirements.txt
```
2. Download the 4.1.0 version of [tesseract](https://digi.bib.uni-mannheim.de/tesseract/)
3. Extract the files into executable (ex: 7-Zip)
4. Place the extracted files into the *tesseract-ocr* folder at the root of package
5. Download [tessdata](https://github.com/tesseract-ocr/tessdata) or [tessdata_best](https://github.com/tesseract-ocr/tessdata_best)
6. Place the traineddata files into the tessdata folder.
7. Download models from EasyOCR `python -m image_translator.download_model`.
*Note: Sometimes the progress bar stop so put a character on terminal*

### Linux
1. Clone the repositoy
```
git clone https://github.com/A2va/ImageTranslator.git
python -m pip install easyocr
python -m pip install craft-text-detector
python -m pip install -r requirements.txt
```
2. Install tesseract (v4.1.0)
3. Download [tessdata](https://github.com/tesseract-ocr/tessdata) or [tessdata_best](https://github.com/tesseract-ocr/tessdata_best)
4. Place the traineddata files into the tessdata folder ('whereis tesseract').
5. Download models from EasyOCR `python -m image_translator.download_model`.
*Note: Sometimes the progress bar stop so put a character on terminal*