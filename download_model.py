import image_translator.model.model_easyocr as easyocr
import image_translator.model.model_tesseract as tesseract
import getopt, sys

short_options = "m:"
long_options = ["mode="]

if __name__ == "__main__":

    args = sys.argv
    args = args[1:]

    try:
        arguments, values = getopt.getopt(args, short_options, long_options)
    except getopt.error as err:
        print (str(err))
        sys.exit(2)

    for arg, value in arguments:
        if arg in ("-m", "--mode"):
            if value=='tesseract':
                tesseract.download_models()
            elif value=='easyocr':
                easyocr.download_models()
            elif value=='all':
                print('Downlaod all models')
            else:
                print("Error: Wrong argument value")
                easyocr.download_models()
                tesseract.download_models()
        else:
            print ("Error: Wrong argument")
