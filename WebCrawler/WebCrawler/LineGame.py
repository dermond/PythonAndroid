# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 12:23:27 2021

@author: dermo
"""
from ppadb.client import Client as AdbClient
import time
import pytesseract
from PIL import Image, ImageEnhance
import io
import os
import ddddocr
import subprocess
import cv2
import numpy as np
from paddleocr import PaddleOCR #paddlepaddle

ocr = ddddocr.DdddOcr()
Pocr = PaddleOCR(use_angle_cls=False, lang='ch')  # lang='ch' 支援

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


    # 轉換為灰階
    gray_img = img.convert("L")

     # 保存到当前工作目录
    gray_img.save(os.path.join(os.getcwd(), 'full_screen.png'))

    
    
    subprocess.run(["adb", "exec-out", "screencap", "-p", ">", "screen.png"], shell=True)


    return gray_img

def crop_image(img, start_point, end_point):
    try:

        left, top = start_point
        right, bottom = end_point

        # 確保裁剪範圍在圖片範圍內
        img_width, img_height = img.size
        left = max(0, min(left, img_width))
        top = max(0, min(top, img_height))
        right = max(left, min(right, img_width))
        bottom = max(top, min(bottom, img_height))

        cropped_img = img.crop((left, top, right, bottom))
         # 保存到当前工作目录
        cropped_img.save(os.path.join(os.getcwd(), 'cropped_image.png'))
    except:
        cropped_img = None 
    return cropped_img

def ddddocr_image(img):
    try:
        image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
        result = ocr.classification(image)
    except:
        result = ""
    return result

def pytesseract_image(img):
   try:
       
        # 進行影像預處理
        img = img.convert("L")  # 轉為灰階，去除顏色雜訊

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)  # 提高對比度（數值可調整）

        # 進行 OCR 辨識，僅識別 `>` 等符號
        custom_config = r'-c tessedit_char_whitelist=">0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" --psm 6'
        result = pytesseract.image_to_string(img, config=custom_config)

   except Exception as e:
        print(f"發生錯誤: {e}")
        result = ""

   return result.strip()  # 去除前後空白字元

def paddleocr_image(img_path):
    if img_path == None:
        return "" 
    full_path = os.path.join(os.getcwd(),  'cropped_image.png')
    results = Pocr.ocr(full_path, cls=True)
    # 組合所有辨識到的文字
    text = '\n'.join([ line[1][0] for block in results for line in block ])
    return text

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

def adb_tap(x, y):
    """發送 ADB 點擊指令"""
    os.system(f"adb shell input tap {x} {y}")

def solve_sudoku():

    start_row=6
    start_col=1


    def should_fill(row, col):
        # 依 row/col 排序判斷是否已到起始格
        if row > start_row:
            return True
        if row < start_row:
            return False
        # row == start_row
        return col >= start_col

    # --- 座標設定 ---
    # 棋盤起始與結束座標
    start_x, start_y = 95, 600
    end_x, end_y = 990, 1480
    
    # 計算間距 (95到990分8個間隔, 600到1480分8個間隔)
    step_x = (end_x - start_x) / 8
    step_y = (end_y - start_y) / 8
    
    # 下方數字列座標 (1~9)
    num_start_x = 80
    num_y = 2107
    num_step_x = (1007 - 80) / 8

    print("開始自動填入數獨...")

    for cell in solution_data:
        row, col, val = cell
        
        # 只從指定起點開始做
        if not should_fill(row, col):
            continue

        # 基本防呆
        if not (1 <= val <= 9):
            print(f"略過 [{row},{col}] val={val}（不在1~9）")
            continue

        # 1. 計算該格子的畫面座標
        target_x = int(start_x + (col - 1) * step_x)
        target_y = int(start_y + (row - 1) * step_y)
        
        # 2. 計算下方對應數字的座標
        val_x = int(num_start_x + (val - 1) * num_step_x)
        
        # 3. 執行點擊：先點位置，再點數字
        print(f"填寫 [{row}, {col}] 為 {val} -> 座標({target_x}, {target_y})")
        adb_tap(target_x, target_y)
        time.sleep(1) # 稍微延遲避免手機反應不及
        adb_tap(val_x, num_y)
        time.sleep(1)

    print("填寫完成！")

if __name__ == '__main__':

  device, client = connect()

  #目前按鈕特性 是給 google pixel 8a用
  # 

  # 數獨解答資料 (僅填入空白格)
  solution_data = [
  [1,1,1],[1,2,5],[1,3,4],[1,4,3],[1,5,2],[1,6,6],[1,7,8],[1,8,7],[1,9,9],
  [2,1,9],[2,2,2],[2,3,8],[2,4,4],[2,5,7],[2,6,1],[2,7,3],[2,8,5],[2,9,6],
  [3,1,6],[3,2,7],[3,3,3],[3,4,9],[3,5,5],[3,6,8],[3,7,1],[3,8,2],[3,9,4],
  [4,1,4],[4,2,8],[4,3,6],[4,4,5],[4,5,3],[4,6,2],[4,7,9],[4,8,1],[4,9,7],
  [5,1,3],[5,2,1],[5,3,7],[5,4,8],[5,5,9],[5,6,4],[5,7,2],[5,8,6],[5,9,5],
  [6,1,2],[6,2,9],[6,3,5],[6,4,1],[6,5,6],[6,6,7],[6,7,4],[6,8,8],[6,9,3],
  [7,1,8],[7,2,6],[7,3,9],[7,4,7],[7,5,1],[7,6,3],[7,7,5],[7,8,4],[7,9,2],
  [8,1,5],[8,2,4],[8,3,2],[8,4,6],[8,5,8],[8,6,9],[8,7,7],[8,8,3],[8,9,1],
  [9,1,7],[9,2,3],[9,3,1],[9,4,2],[9,5,4],[9,6,5],[9,7,6],[9,8,9],[9,9,8]
]

  solve_sudoku()
















