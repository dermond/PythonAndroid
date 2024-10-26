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

def connect():

  client = AdbClient(host='127.0.0.1', port=5037)

  devices = client.devices()
  if len(devices) == 0:
    print('No devices')
    quit()

  device = devices[0]
  print(f'Connected to {device}')

  return device, client

def tap(device, position):
    device.shell(f'input tap {position}')
    

def select_from_dropdown(device, dropdown_position, text,option_position):
    # 點擊下拉清單以打開
    tap(device, dropdown_position)
    time.sleep(1.0)  # 等待輸入框激活
    
    # 輸入文字
    input_characters(device, text)
    time.sleep(1.0)  # 等待輸入框激活
    # 選擇清單中的選項
    tap(device, option_position)
    
def input_text_in_field(device, field_position, text):
    # 點擊輸入框位置以激活
    tap(device, field_position)
    time.sleep(0.5)  # 等待輸入框激活
    # 輸入文字
    input_characters(device, text_to_input)
    
    
def input_characters(device, characters):
    keycode_map = {
        '0': 7, '1': 8, '2': 9, '3': 10, '4': 11, '5': 12,
        '6': 13, '7': 14, '8': 15, '9': 16,
        'a': 29, 'b': 30, 'c': 31, 'd': 32, 'e': 33, 'f': 34,
        'g': 35, 'h': 36, 'i': 37, 'j': 38, 'k': 39, 'l': 40,
        'm': 41, 'n': 42, 'o': 43, 'p': 44, 'q': 45, 'r': 46,
        's': 47, 't': 48, 'u': 49, 'v': 50, 'w': 51, 'x': 52,
        'y': 53, 'z': 54,
        'A': 29, 'B': 30, 'C': 31, 'D': 32, 'E': 33, 'F': 34,
        'G': 35, 'H': 36, 'I': 37, 'J': 38, 'K': 39, 'L': 40,
        'M': 41, 'N': 42, 'O': 43, 'P': 44, 'Q': 45, 'R': 46,
        'S': 47, 'T': 48, 'U': 49, 'V': 50, 'W': 51, 'X': 52,
        'Y': 53, 'Z': 54,
        ' ': 62,  # 空格
        '\t': 61,  # Tab (用于跳到下一个输入框)
    }
    
    for char in characters:
        if char in keycode_map:
            input_keyevent(device, keycode_map[char])
        else:
            print(f"Character '{char}' is not supported.")
     
def input_keyevent(device, keycode):
    device.shell(f'input keyevent {keycode}')
    
def swipe_to_position(device, start, end, duration=500):
    device.shell(f'input swipe {start} {end} {duration}')
    time.sleep(1)  # 等待滑动完成
    
def capture_screenshot(device):
    result = device.screencap()
    img = Image.open(io.BytesIO(result))
     # 保存到当前工作目录
    img.save(os.path.join(os.getcwd(), 'full_screen.png'))
    return img

def crop_image(img, start_point, end_point):
    left, top = start_point
    right, bottom = end_point
    cropped_img = img.crop((left, top, right, bottom))
     # 保存到当前工作目录
    cropped_img.save(os.path.join(os.getcwd(), 'cropped_image.png'))
    return cropped_img

def ddddocr_image(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
    result = ocr.classification(image)
    return result

def pytesseract_image(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
    result = pytesseract.image_to_string(img)
    return result

def check_error_code(text, error_code):
    # 检查文本中是否包含指定的错误码
    if error_code in text:
        return True
    return False

if __name__ == '__main__':

  device, client = connect()

  for _ in range(5):
      
      #轉帳
      #tap(device, "676 1281")
      tap(device, "676 1603")
      time.sleep(1.0)
  
      #手機轉帳
      tap(device, "886 334")
      time.sleep(1.0)

       #滑動
      swipe_start = '500 500'
      swipe_end = '500 2000'
      swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
      time.sleep(1.0)

      dropdown_position = '474 1200'  # 下拉清單的位置
      #text_to_input = '008'  # 輸入的文字 #華南銀行
      #text_to_input = '700'  # 輸入的文字 #郵局
      text_to_input = '007'  # 輸入的文字 #第一銀行
      option_position = '454 1030'    # 選擇的選項的位置

      # 從下拉清單中選擇
      select_from_dropdown(device, dropdown_position,text_to_input, option_position)
      time.sleep(1.0)

      #輸入帳號
      input_characters(device, "0926865002")
      time.sleep(1.0)
  
      #滑動
      swipe_start = '500 1300'
      swipe_end = '500 500'
      swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
      time.sleep(2.0)
  
      #金額
      tap(device, "262 690")
      input_characters(device, "888")
      time.sleep(1.0)

      #滑動
      swipe_start = '500 1500'
      swipe_end = '500 500'
      swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
      time.sleep(1.0)

      #選擇卡片
      tap(device, "558 1058")
      time.sleep(1.0)
      #tap(device, "582 1382") #第一銀行(1)
      #tap(device, "582 1882") #第一銀行(2)
      #tap(device, "582 1636") #華南
      tap(device, "582 2125") #郵局
      time.sleep(1.0)
  
  
      #輸入密碼
      tap(device, "387 1338")
      input_characters(device, "9393695")
  
      #取消輸入框
      tap(device, "798 2198")
      time.sleep(1.0)
      tap(device, "824 2341")
      time.sleep(1.0)

      while True:
          #圖片驗證
          start_point = (117, 1524)  # 起始坐標 (x, y)
          end_point = (496, 1695)    # 結束坐標 (x, y)

          img = capture_screenshot(device)
          cropped_img = crop_image(img, start_point, end_point)
          resulttext = ddddocr_image(cropped_img)

          #輸入你的驗證碼
          input_characters(device, resulttext)
          time.sleep(1.0)
  
          #確認
          tap(device, "492 2150")
          time.sleep(1.0)
  

          #錯誤視窗判斷
          start_point = (103, 940)  # 起始坐標 (x, y)
          end_point = (715, 1400)    # 結束坐標 (x, y)

          img = capture_screenshot(device)
          cropped_img = crop_image(img, start_point, end_point)
          resulttext = pytesseract_image(cropped_img)
  
          error_code = '8101'
          if check_error_code(resulttext, error_code):
            print(f"Error code {error_code} found in the image!")
            #確認
            tap(device, "855 1355")
            time.sleep(1.0)
          
          else:
            print(f"Error code {error_code} not found in the image.")
            time.sleep(3.0)
            break



      tap(device, "515 2160")
      time.sleep(3.0)
  
      error_code = '9999'
      if check_error_code(resulttext, error_code):
        print(f"Error code {error_code} found in the image!")
        #確認
        tap(device, "855 1355")
        time.sleep(1.0)
          
      # else:
      #   print(f"Error code {error_code} not found in the image.")
      #   time.sleep(3.0)
      
      

      tap(device, "847 1380")
      time.sleep(3.0)
  
      tap(device, "321 2162")
      time.sleep(1.0)
  
  
  

    