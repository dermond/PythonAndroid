# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 12:23:27 2021

@author: dermo
"""
from ppadb.client import Client as AdbClient
import time
import pytesseract
from PIL import Image
import io
import os

import ddddocr

ocr = ddddocr.DdddOcr()

def pytesseract_image():
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
    # 识别验证码
    result = ocr.classification(image)

    #result = pytesseract.image_to_string(image)
    return result

if __name__ == '__main__':

  
    pytesseract_image()