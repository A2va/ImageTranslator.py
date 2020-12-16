import image_translator.model.model_easyocr as easyocr
import image_translator.model.model_tesseract as tesseract

if __name__ == "__main__":
    easyocr.download_models()
    tesseract.download_models()