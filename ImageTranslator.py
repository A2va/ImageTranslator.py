import cv2
import pytesseract
import numpy as np
import io
import craft_text_detector as craft_detector
from text_binarization import textBin 

from PIL import ImageGrab
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from googletrans import Translator

from urllib.request import urlretrieve


pytesseract.pytesseract.tesseract_cmd = 'D:/Programs/tesseract-ocr/tesseract.exe'
tra =Translator()

class ImageTranslator():
    """The main class of the tranlsator 
    
    Args: img This can be file,bytes or URL
    """
    def __init__(self,img):

        self.img= self.__reformat_input(img)
        self.img_out=img.copy()
        self.paragraph=[]
        self.text=[]
        self.mask_paragraph=None

    def processing(self):
        self.detect_text()
        self.detect_paragraph()

        for paragraph in self.paragraph:
            x=paragraph['x']
            y=paragraph['y']
            w=paragraph['w']
            h=paragraph['h']
            text =self.__run_tesserract(paragraph['image'])

            if text['string'] !='':
                cv2.rectangle(self.img_out, (x,y), (x+w, y+h), (255, 255,255), -1)
                self.__translate_text(text,par,w)
                self.__apply_translation()

    def __detect_text(self):
        """
        Return a mask from the text location
        """
        blank_image = np.zeros((self.img.shape[0],self.img.shape[1],1), np.uint8)
        prediction_result=self.__craft(self.img)
        boxes=prediction_result['boxes']

        for box in boxes:
            point1=tuple(box[0])
            point2=tuple(box[2])
            cv2.rectangle(blank_image, point1, point2, 255, -1)

        self.mask_paragraph=blank_image

    def __detect_paragraph(self):
        par_list=[]
        img=img_in.copy()

        #Find contours
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))  
        dilated = cv2.dilate(self.mask_paragraph, kernel, iterations=9) 
        contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

        for contour in contours:

            [x, y, w, h] = cv2.boundingRect(contour)
            cropped=img[y :y +  h , x : x + w]

            cropped=cv2.bitwise_and(cropped,self.mask_paragraph[y :y +  h , x : x + w])

            #Apply binarization
            binary=textBin(cropped)
            cropped=binary.processing()
            self.paragraph.append({
                'image':cropped,
                'x':x,
                'y':y,
                'w':w,
                'h':h
            })
        
    def __run_tesserract(self,img):
        boxes = pytesseract.image_to_data(img)
        string=''
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
    def __run_easyocr(self,img):
        reader = easyocr.Reader(['en'])
        result = reader.readtext(img)
        #1|----------------------------|2
        # |                            |
        #4|----------------------------|3
        #[[[x1,y1],[x2,y2][x3,y3],[x4,y4],'I am currently working in an image translator project.'],0.031xxx]
        x=result[0][0][0][0]
        y=result[0][0][0][1]
        w=result[0][0][2][0]-x
        h=result[0][0][2][1]-y
        string=''
        for res in result:
            string+=res[1]
        return {
            'x':x,
            'y':y,
            'w':w,
            'h':h,
            'string':string
        }

    def __craft(self,img):
        """
        Return the text location
        """
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

        return prediction_result

    def __reformat_input(self,image):
        """
        Reformat the input image
        """
        if type(image) == str:
            if image.startswith('http://') or image.startswith('https://'):
                #Read bytes from url
                image=urllib.request.urlopen(image).read()

            nparr = np.frombuffer(image, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif type(image) == np.ndarray:
            if len(image.shape) == 2: # grayscale
                img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif len(image.shape) == 3 and image.shape[2] == 3: # BGRscale
                img = image
            elif len(image.shape) == 3 and image.shape[2] == 4: # RGBAscale
                img = image[:,:,:3]
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            print('[Warning] Invalid input type. Suppoting format = string(file path or url), bytes, numpy array')
        return img

    def __text_wrap(text, font, max_width):
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

    def __translate_text(self,paragraph):
        x=string['x'] + paragraph['x']-45
        y=string['y'] + paragraph['y']-20
        w=string['w']
        h=string['h']
        string_str= tra.translate(string['string'],dest='fr').text

        self.text.append({
            'text':string['string'],
            'translate':string_str,
            'x':x,
            'y':y,
            'w':w,
            'h':h,
            'max_width':paragraph['w']
        })
    
    def __apply_translation(self,max_width):
        im_pil = Image.fromarray(self.img_out)
        draw = ImageDraw.Draw(im_pil)

        font_file_path = 'Cantarell.ttf'
        font_size=int(h*1.1)
        font = ImageFont.truetype(font_file_path, size=font_size, encoding="unic")

        for tt in self.text:
            lines = text_wrap(tt['translate'], font,max_width)
            line_height = font.getsize('hg')[1]
            for line in lines:
                draw.text((x, y), line, fill=(0,0,0), font=font)
                y = y + line_height

            self.img_out = np.asarray(im_pil)




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



