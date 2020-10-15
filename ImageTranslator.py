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

import urllib

pytesseract.pytesseract.tesseract_cmd = 'D:/Programs/tesseract-ocr/tesseract.exe'
tra =Translator()

#https://iso639-3.sil.org/

TRANS_LANG={
        #Google Trans
    'afr': ['af']                               #Afrikaans
    'amh': ['am']                               #Amharic
    'ara': ['ar']                               #Arabic
    'aze': ['az']                               #Azerbaijani

    'bel': ['be']                               #Belarusian
    'ben': ['bn']                               #Bengali
    'bos': ['bs']                               #Bosnian
    'bul': ['bg']                               #Bulgarian

    'cat': ['ca']                               #Catalan
    'ceb': ['ceb']                              #Cebuano
    'ces': ['cs']                               #Czech
    'chi_sim': ['zh-cn']                        #Chinese (simplified)
    'chi_tra': ['zh-tw']                        #Chinese (traditional
    'cos': ['co']                               #Corsican
    'cym': ['cy']                               #Welsh

    'dan': ['da']                               #Danish
    'deu': ['de']                               #German

    'ell': ['el']                               #Greek
    'eng': ['en']                               #English
    'est': ['et']                               #Estonian
    'eus': ['eu']                               #Basque

    'fas': ['fa']                               #Persian
    'fin': ['fi']                               #Finnish
    'fra': ['fr']                               #French
    'fry': ['fy']                               #Frisian

    'gla': ['gd']                               #Scottish Gaelic
    'gle': ['ga']                               #Irish
    'glg': ['gl']                               #Galician
    'guj': ['gu']                               #Gujarati

    'hat': ['ht']                               #Haitian
    'heb': ['iw']                               #Hebrew
    'hin': ['hi']                               #Hindi
    'hrv': ['hr']                               #Croatian
    'hun': ['hu']                               #Hungarian
    'hye': ['hy']                               #Armenian

    'ind': ['id']                               #Indonesian
    'isl': ['is']                               #Icelandic
    'ita': ['it']                               #Italian

    'jav': ['jw']                               #Javanese
    'jpn': ['ja']                               #Japanese

    'kan': ['ka']                               #Kannada
    'kat': ['ka']                               #Georgian
    'kaz': ['kk']                               #Kazakh
    'khm': ['km']                               #Khmer
    'kir': ['ky']                               #Kyrgyz
    'kmr': ['ku']                               #Kurdish
    'kor': ['ko']                               #Korean

    'lao': ['lo']                               #Lao
    'lat': ['la']                               #Latin
    'lav': ['lv']                               #Latvian
    'lit': ['lt']                               #Lithuanian
    'ltz': ['lb']                               #Luxembourgish

    'mal': ['ml']                               #Malayalam
    'mar': ['mr']                               #Marathi
    'mkd': ['mk']                               #Macedonian
    'mlt': ['mt']                               #Maltese
    'mon': ['mn']                               #Mongolian
    'mri': ['mi']                               #Maori
    'msa': ['ms']                               #Malay
    'mya': ['my']                               #Burmese

    'nep': ['ne']                               #Nepali
    'nld': ['nl']                               #Dutch
    'nor': ['no']                               #Norwegian

    'ory': ['or']                               #Odiya

    'pol': ['pl']                               #Polish
    'por': ['pt']                               #Portuguese
    'pus': ['ps']                               #Pashto

    'ron': ['ro']                               #Romanian
    'rus': ['ru']                               #Russian

    'slk': ['sk']                               #Slovak
    'slv': ['sl']                               #Slovenian
    'snd': ['sd']                               #Sindhi
    'spa': ['es']                               #Spanish
    'sqi': ['sq']                               #Albanian
    'srp_latn': ['sr']                          #Serbian
    'sun': ['su']                               #Sundase
    'swa': ['sw']                               #Swahili
    'swe': ['sv']                               #Swedish
    'sna': ['sn']                               #Shona
    'sin': ['si']                               #Sinhala

    'tam': ['ta']                               #Tamil
    'tgk': ['tg']                               #Tajik
    'tha': ['th']                               #Thai
    'tur': ['tr']                               #Turkish

    'uig': ['ug']                               #Uighur
    'ukr': ['uk']                               #Ukrainian
    'urd': ['ur']                               #Urdu
    'uzb': ['uz']                               #Uzbek
    'vie': ['vi']                               #Vietnamese

    'yid': ['yi']                               #Yiddish
    'yor': ['yo']                               #Yoruba

    #'zul': ['zu']                              #Zulu
    #'xho': ['xh']                              #Xhosa
    #'te': ['te']                               #Telegu
    #'som': ['sl']                              #Somali
    #'st':['st']                                #Sesotho
    #'pan': ['']                                #Punjabi
    #'nya': ['ny']                              #Chichewa
    #'mlg': ['mg']                              #Malagasy
    #'ibo': ['ib']                              #Igbo
    #'hmn': ['hmn']                             #Hmong
    #'epo': ['eo']                              #Esperanto
    #'haw': ['hw']                              #Hawaiian
    #'fil': ['tl']                              #Filipino
    #'hau': ['ha']                              #Hausa
    #'smo': ['sm']                              #Samoan
}

OCR_LANG={
            #Tesseract #EasyOCR
    'abq':['invalid','abq']                     #Abaza
    'ady':['invalid','ady']                     #Adyghe
    'anp':['invalid','ang']                     #Angika
    'afr': ['afr','af']                         #Afrikaans
    'amh': ['amh','invalid']                    #Amharic
    'ara': ['ara','ar']                         #Arabic
    'asm': ['asm','as']                         #Assamese
    'ava':['invalid','ava']                     #Avar
    'aze': ['aze','az']                         #Azerbaijani
    'aze_cyrl': ['aze_cyrl','invalid']  
    'bih': ['invalid','bh']                     #Bihari      
    'bel': ['bel','be']                         #Belarusian
    'ben': ['ben','bn']                         #Bengali
    'bho': ['invalid','bho']                    #Bhojpuri
    'bod': ['bod','invalid']                    #Tibetan
    'bos': ['invalid','bos']                    #Bosnian
    'bul': ['bul','bg']                         #Bulgarian
    'cat': ['cat','invalid']                    #Catalan
    'ceb': ['ceb','invalid']                    #Cebuano 
    'ces': ['ces','cz']                         #Czech
    'che': ['invalid','che']                    #Chechen
    'chi_sim': ['chi_sim','ch_sim']             #Sinplified Chinese
    'chi_sim_vert': ['chi_sim_vert','invalid']  #Vertical Simplified Chinese
    'chi_tra':['chi_tra','ch_tra']              #Traditional Chinese 
    'chi_tra_vert': ['chi_tra_vert','invalid']  #Traditional Chinese verctical 
    'chr': ['chr','invalid']                    #Cherokee
    'cos': ['cos','invalid']                    #Corsican
    'cym': ['invalid','cy']                     #Welsh
    'sim': ['sim','invalid']                    #Mende (Papua New Guinea)
    'dan': ['dan','da']                         #Danish
    'dar': ['invalid','dar']                    #Dargwa
    'deu': ['deu','de']                         #German
    'div': ['div','invalid']                    #Divehi
    'dzo': ['dzo','invalid']                    #Dzongkha
    'ell': ['ell','invalid']                    #Mordern Greek
    'eng': ['eng','en']                         #English
    'enm': ['enm','invalid']                    #Middle English
    'est': ['est','et']                         #Estonian
    'eus': ['eus','invalid']                    #Basque
    'fao': ['fao','invalid']                    #Faroese
    'fas': ['fas','fa']                         #Persian
    'fin': ['fin','invalid']                    #Finnish
    'fra': ['fra','fr']                         #French
    'frk': ['frk','invalid']                    #Frankish 
    'frm': ['frm','invalid']                    #Middle French
    'fry': ['fry','invalid']                    #Western Frisian
    'gla': ['gla','invalid']                    #Scottish Gaelic
    'gle': ['gle','ga']                         #Irish
    'glg': ['glg','invalid']                    #Galician
    'gom': ['invalid','gom']                    #Goan Konkani
    'grc': ['grc','invalid']                    #Ancient Greek
    'quj': ['quj','invalid']                    #Gujuarati
    'hat': ['hat','invalid']                    #Haitian
    'heb': ['heb','invalid']                    #Hebrew
    'hin': ['hin','hi']                         #Hindi
    'hrv': ['hrv','hr']                         #Croatian
    'hun': ['hun','hu']                         #Hungarian
    'hye': ['hye','invalid']                    #Armenian
    'iku': ['iku'.'invalid']                    #Inuktitut 
    'ind': ['ind','id']                         #Indonesian
    'inh': ['invalid','inh']                    #Ingush
    'isl': ['isl','is']                         #Icelandic
    'ita': ['ita','it']                         #Italian
    'ita_old': ['ita_old','invalid']            #Old Italian
    'jav': ['jav','invalid']                    #Javanese
    'jpn': ['jpn','jp']                         #Japanese
    'jpn_vert': ['jpn_vert','invalid']          #Vertical Japanese
    'kan': ['kan','invalid']                    #Kannada
    'kat': ['kat','invalid']                    #Georgian
    'kat_old': ['kat_old','invalid']            #Old Georgian
    'kaz': ['kaz','invalid']                    #Kazakh
    'kdb': ['invalid','kdb']                    #Kabardian
    'khm': ['khm','invalid']                    #Khmer
    'kir': ['kir','invalid']                    #Kirghiz 
    'kmr': ['kmr','ku']                         #Northern Kurdish
    'kor': ['kor','ko']                         #Korean
    'kor_vert': ['kor_vert','invalid']          #Vertical Korean
    'lao': ['lao','invalid']                    #Lao
    'lat': ['lat','la']                         #Latin
    'lav': ['lav','lv']                         #Latvian
    'lbe': ['invalid','lbe']                    #Lak
    'lez': ['invalid','lez']                    #Lezghian
    'lit': ['lit','lt']                         #Lithuanian 
    'ltz': ['ltz','invalid']                    #Luxembourgish 
    'mai': ['invalid','mai']                    #Maithili
    'mah': ['invalid','mah']                    #Magahi
    'mal': ['mal','invalid']                    #Malayalam
    'mar': ['mar','mr']                         #Marathi 
    'mkd': ['mlt','invalid']                    #Macedonian 
    'mlt': ['mlt','mt']                         #Maltese 
    'mon': ['mon','mn']                         #Mongolian 
    'mri': ['mri','mi']                         #Maori 
    'msa': ['msa','ms']                         #Malay 
    'mya': ['mya','invalid']                    #Burmese 
    'nep': ['nep','ne']                         #Nepali 
    'new': ['invalid','new']                    #Newari
    'nld': ['nld','nl']                         #Dutch
    'nor': ['nor','no']                         #Norwegian
    'oci': ['oci','oc']                         #Occitan 
    'ory': ['ori','invalid']                    #Oriya 
    'pan': ['pan','invalid']                    #Panjabi 
    'pol': ['pol','pl']                         #Polish 
    'por': ['por','pt']                         #Portuguese 
    'pus': ['pus','invalid']                    #Pushto 
    'que': ['que','invalid']                    #Quechua 
    'ron': ['ron','ro']                         #Romanian 
    'rus': ['rus','ru']                         #Russian
    'san': ['san','invalid']                    #Sanskrit
    'sck': ['invalid','sck']                    #Nagpuri
    'sin': ['sin','invalid']                    #Sinhala 
    'slk': ['slk','sk']                         #Slovak 
    'slv': ['slv','sl']                         #Slovenian 
    'snd': ['snd','invalid']                    #Sindhi 
    'spa': ['spa','es']                         #Spanish 
    'spa_old': ['spa_old']                      #Old Spanish
    'sqi': ['sqi','sq']                         #Albanian 
    'srp': ['srp','rs_cyrillic']                #Serbian 
    'srp_latn': ['srp_latn','rs_latin']         #Latin Serbian
    'sun': ['sun','invalid']                    #Sundanese 
    'swa': ['swa','sw']                         #Swahili 
    'swe': ['swe','sv']                         #Swedish
    'syr': ['syr','invalid']                    #Syriac
    'tab': ['invalid','tab']                    #Tabassaran
    'tam': ['tam','ta']                         #Tamil
    'tat': ['tat','invalid']                    #Tatar
    'tel': ['tgk','invalid']                    #Telugu
    'tgk': ['tgk','invalid']                    #Tajiik
    'tha': ['tha','th']                         #Thai 
    'tir': ['tir','invalid']                    #Tigrinya
    'tgl': ['invalid','tl']                     #Tagalog 
    'ton': ['ton','invalid']                    #Tonga 
    'tur': ['tur','tr']                         #Turkish 
    'uig': ['uig','ug']                         #Uighur 
    'ukr': ['ukr','uk']                         #Ukrainian 
    'urd': ['urd','ur']                         #Urdu
    'uzb': ['uzb','uz']                         #Uzbek
    'urb_cyrl': ['urb_cyrl','invalid']          #Cyrillic Uzbek
    'vie': ['vie','vi']                         #Vietnamese 
    'yid': ['yid','invalid']                    #Yiddish 
    'yor': ['yor','invalid']                    #Yoruba 
}

class ImageTranslator():
    """
    The main class of the translator 
    
    Args: img This can be file,bytes or URL
        ocr: 'EasyOCR' or 'Tesseract'
    """
    def __init__(self,img,ocr):

        self.img= self.__reformat_input(img)
        self.img_out=self.img.copy()
        self.text=[]
        self.mask_paragraph=None
        self.ocr=ocr

    def processing(self):
        self.mask_paragraph=self.__detect_text(self.img)
        paragraphs=self.__detect_paragraph()
        #Apply Binarization and ocr
        for paragraph in paragraphs:
            binary=textBin(paragraph['image'])
            paragraph['image']=binary.processing()

            self.text.append(self.__run_ocr(paragraph))

        for i in range(0,len(self.text)):
            x=self.text[i]['x']
            y=self.text[i]['y']
            w=self.text[i]['w']
            h=self.text[i]['h']
            if self.text[i]['string'] !='':
                cv2.rectangle(self.img_out, (x,y), (x+w, y+h), (255, 255,255), -1)
                self.text[i]=self.__translate_text(self.text[i])
                self.__apply_translation(self.text[i])


    def __detect_text(self,img):
        """
        Return a mask from the text location
        """
        blank_image = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
        prediction_result=self.__craft(img)
        boxes=prediction_result['boxes']

        for box in boxes:
            point1=tuple(box[0])
            point2=tuple(box[2])
            cv2.rectangle(blank_image, point1, point2, (255,255,255), -1)

        return blank_image

    def __detect_paragraph(self):
        """
        Return a dict with cropped paragraph and location
        """
        paragraph=[]
        img=self.img.copy()

        #Find contours
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))  
        dilated = cv2.dilate(cv2.cvtColor(self.mask_paragraph,cv2.COLOR_BGR2GRAY), kernel, iterations=9) 
        contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

        for contour in contours:

            [x, y, w, h] = cv2.boundingRect(contour)
            cropped=img[y :y +  h , x : x + w]

            cropped=cv2.bitwise_and(cropped,self.mask_paragraph[y :y +  h , x : x + w])

            #Apply binarization
            paragraph.append({
                'image':cropped,
                'x':x,
                'y':y,
                'w':w,
                'h':h
            })
            return paragraph
        
    def __run_ocr(self,paragraph):
        """
        Run OCR between Tesseract and EasyOCR
        """
        if self.ocr=='EasyOCR':
            return self.__run_easyocr(paragraph)
        elif self.ocr=='Tesseract':
            return self.__run_tesserract(paragraph)

    def __run_tesserract(self,paragraph):
        """
        Run tesseract OCR
        """
        boxes = pytesseract.image_to_data(paragraph['image'])
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
                'x':x+paragraph['x']-45,
                'y':y+paragraph['y']-20,
                'w':w,
                'h':h,
                'string':string,
                'image': paragraph['image'],
                'max_width':paragraph['w']
                }
    def __run_easyocr(self,paragraph):
        """
        Run EasyOCR
        """
        reader = easyocr.Reader(['en'])
        result = reader.readtext(paragraph['image'])
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
            'x':x+paragraph['x']-45,
            'y':y+paragraph['y']-20,
            'w':w,
            'h':h,
            'string':string,
            'image':paragraph['image'],
            'max_width':paragraph['w']

        }

    def __craft(self,img):
        """
        Return a predication of text location
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
            if len(image.shape) == 2: 
                img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif len(image.shape) == 3 and image.shape[2] == 3:
                img = image
            elif len(image.shape) == 3 and image.shape[2] == 4:
                img = image[:,:,:3]
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            print('[Warning] Invalid input type. Suppoting format = string(file path or url), bytes, numpy array')
        return img

    def __text_wrap(text, font, max_width):
        """
        Wrap the into multiple lines
        """
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

    def __translate_text(self,text):
        """
        Translate the text
        """
        string= tra.translate(text['string'],dest='fr').text

        text['translated_string']=string
        return text
    
    def __apply_translation(self,text):
        """
        Apply the translation on img_out
        """

        im_pil = Image.fromarray(self.img_out)
        draw = ImageDraw.Draw(im_pil)

        font_file_path = 'Cantarell.ttf'
        font_size=int(h*1.1)
        font = ImageFont.truetype(font_file_path, size=font_size, encoding="unic")

        lines = text_wrap(text['translated_string'], font,text['max_width'])
        line_height = font.getsize('hg')[1]
        for line in lines:
            draw.text((text['x'], text['y']), line, fill=(0,0,0), font=font)
            y = y + line_height
        self.img_out = np.asarray(im_pil)



test=ImageTranslator('https://i.stack.imgur.com/vrkIj.png','Tesseract')
test.processing()

