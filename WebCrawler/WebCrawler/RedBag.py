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
import subprocess

ocr = ddddocr.DdddOcr()

def connect(index = 0):

  client = AdbClient(host='127.0.0.1', port=5037)

  devices = client.devices()
  if len(devices) == 0:
    print('No devices')
    quit()

  device = devices[index]
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
    
def input_text(device, text):
    device.shell(f'input text {text}')
    
def swipe_to_position(device, start, end, duration=500):
    device.shell(f'input swipe {start} {end} {duration}')
    time.sleep(1)  # 等待滑动完成
    
def capture_screenshot(device):
    result = device.screencap()
    img = Image.open(io.BytesIO(result))
     # 保存到当前工作目录
    img.save(os.path.join(os.getcwd(), 'full_screen.png'))

    
    subprocess.run(["adb", "exec-out", "screencap", "-p", ">", "screen.png"], shell=True)


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

def get_current_ime():
    try:
        result = subprocess.run(
            ["adb", "shell", "ime", "list", "-s"],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def switch_to_english():
    target_ime = "com.google.android.inputmethod.latin/.LatinIME"
    current_ime = get_current_ime()

    if current_ime == target_ime:
        print("Input method is already set to English (US).")
    else:
        try:
            subprocess.run(["adb", "shell", "ime", "set", target_ime], check=True)
            print(f"Successfully switched to {target_ime}")
        except subprocess.CalledProcessError:
            print("Failed to switch input method.")



if __name__ == '__main__':

  device, client = connect()

  #目前按鈕特性 是給 google pixel 8a用
  # 

  for _ in range(9999):
      
      #轉帳
      tap(device, "950 1410")
      time.sleep(1.0)

      start_point = (875, 776)  # 起始坐標 (x, y)
      end_point = (1040, 875)    # 結束坐標 (x, y)

      img = capture_screenshot(device)
      cropped_img = crop_image(img, start_point, end_point)
      resulttext = pytesseract_image(cropped_img)
      if resulttext.find("TWD 5") > -1 or resulttext.find("TWD 2") > -1:
        tap(device, "42 220 ")
        time.sleep(1.0)
        continue 

      
      tap(device, "874 1269")
      time.sleep(1.0)
      #tap(device, "644 1610")
      #tap(device, "689 1509")
      #time.sleep(1.0)
  