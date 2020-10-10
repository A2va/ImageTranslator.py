import cv2
import pytesseract
import numpy as np

import craft_text_detector as craft_detector
from text_binarization import textBin 

from PIL import ImageGrab
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from googletrans import Translator


pytesseract.pytesseract.tesseract_cmd = 'D:/Programs/tesseract-ocr/tesseract.exe'
tra =Translator()

def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text) 
    else:
        # split the line by spaces to get words
        words = text.split(' ')  
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''         
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word, 
            # add the line to the lines array
            lines.append(line)    
    return lines


def detect_text(img):
    width=img.shape[0]
    height=img.shape[1]
    blank_image = np.zeros((width,height,3), np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if img.shape[0] == 2:
        img = img[0]
    if img.shape[2] == 4:
        img = img[:, :, :3]

    refine_net= craft_detector.load_refinenet_model(cuda=False)
    craft_net = craft_detector.load_craftnet_model(cuda=False)
    prediction_result = craft_detector.get_prediction(image=img,craft_net=craft_net,
    refine_net=refine_net,text_threshold=0.7,link_threshold=0.4,low_text=0.4,cuda=False,
    long_size=1280)  
    boxes=prediction_result['boxes']

    for box in boxes:
        point1=tuple(box[0])
        point2=tuple(box[2])
        cv2.rectangle(blank_image, point1, point2, (255, 255, 255), -1)

    return blank_image


def detect_paragraph(img_in,mask_in):
    par_list=[]
    img=img_in.copy()
    img2gray = cv2.cvtColor(mask_in, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 180, 255, cv2.THRESH_BINARY)
    image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
    ret, new_img = cv2.threshold(image_final, 180, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))  
    dilated = cv2.dilate(new_img, kernel, iterations=9) 

  

    contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    i=0
    mask=mask_in.copy()
    i=0
    for contour in contours:

        [x, y, w, h] = cv2.boundingRect(contour)
        cropped=img[y :y +  h , x : x + w]

        cropped=cv2.bitwise_and(cropped,mask_in[y :y +  h , x : x + w])

        binary=textBin(cropped)
        cropped=binary.processing()
        par_list.append({
            'image':cropped,
            'x':x,
            'y':y,
            'w':w,
            'h':h
        })
    
    return par_list


def get_text(img_in):
    boxes = pytesseract.image_to_data(img_in)
    string=''
    compare_y=0
    compare_y_old=0
    x,y,w,h=(0,0,0,0)
    first=True
    for a,b in enumerate(boxes.splitlines()):
        if a!=0:
            b = b.split()
            if len(b)==12: 
                if first== True:
                    x=int(b[6])
                    y=int(b[7])
                    w =int(b[8])
                    h =int(b[9])
                    first=False
                string=string +str(b[11])+' '
    return {
        'x':x,
        'y':y,
        'w':w,
        'h':h,
        'string':string
    }


def translate_text(img_in,string,par,width):
    x=string['x'] + par['x']-45
    y=string['y'] + par['y']-20
    w=string['w']
    h=string['h']
    font_size=int(h*1.1)
    im_pil = Image.fromarray(img_in)
    draw = ImageDraw.Draw(im_pil)

    string= tra.translate(string['string'],dest='fr').text
    font_file_path = 'Cantarell-Regular.ttf'
    font = ImageFont.truetype(font_file_path, size=font_size, encoding="unic")

    lines = text_wrap(string, font,width)
    line_height = font.getsize('hg')[1]
    for line in lines:
        draw.text((x, y), line, fill=(0,0,0), font=font)
        
        y = y + line_height
    img_in = np.asarray(im_pil)
    return img_in


img = cv2.imread('exemple.jpg')

mask=detect_text(img)

par_list=detect_paragraph(img,mask)
for par in par_list:
    x=par['x']
    y=par['y']
    w=par['w']
    h=par['h']
    text =get_text(par['image'])

    if text['string'] !='':
        cv2.rectangle(img, (x,y), (x+w, y+h), (255, 255,255), -1)
        img=translate_text(img,text,par,w)

cv2.imwrite('out.jpg',img)


###########################################
# Translate
###########################################



