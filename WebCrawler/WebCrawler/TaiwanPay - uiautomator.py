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
import ddddocr #opencv-python==3.4.16.59
import subprocess
from paddleocr import PaddleOCR #paddlepaddle
import cv2
import re
import Service.SettingReader as SettingReader
import threading
import socket
import struct
import uiautomator2 as u2
import traceback

ocr = ddddocr.DdddOcr()
# 建一次 OCR 物件就好，重複呼叫時不用每次都 new
Pocr = PaddleOCR(use_angle_cls=False, lang='ch')  # lang='ch' 支援簡繁中

def connect(serial: str):
    client = AdbClient(host='127.0.0.1', port=5037)

    devices = client.devices()
    if not devices:
        print('No devices')
        quit()

    # 嘗試找出符合 serial 的裝置
    for device in devices:
        print(str(device.serial))
        if device.serial == serial:
            print(f'Connected to {device}')
            return device, client

    # 找不到時回傳第一筆裝置
    fallback_device = devices[0]
    print(f'Device with serial "{serial}" not found, fallback to {fallback_device.serial}')
    #quit()
    return fallback_device, client

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
    try:
        left, top = start_point
        right, bottom = end_point
        cropped_img = img.crop((left, top, right, bottom))
         # 保存到当前工作目录
        cropped_img.save(os.path.join(os.getcwd(), 'cropped_image.png'))
    except Exception as ex:
       crop_image(img, start_point, end_point)
    return cropped_img

def ddddocr_image(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
    result = ocr.classification(image)
    return result

def pytesseract_image(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
    result = pytesseract.image_to_string(img)
    return result

def paddleocr_image(img_path):
    full_path = os.path.join(os.getcwd(), 'cropped_image.png')

    img = cv2.imread(full_path)

    # 加 padding (白邊)
    img = cv2.copyMakeBorder(
        img,
        100, 100, 100, 100,           # top, bottom, left, right
        cv2.BORDER_CONSTANT,
        value=[255, 255, 255]     # 白色背景
    )

    results = Pocr.ocr(img, cls=True)
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

def click_bounds(d, bounds_str):
    # 使用正規表達式抓出四個數字 [left, top][right, bottom]
    nums = re.findall(r'\d+', bounds_str)
    if len(nums) == 4:
        left, top, right, bottom = map(int, nums)
        # 計算中心點
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        
        print(f"🎯 點擊中心點: ({center_x}, {center_y})")
        d.click(center_x, center_y)


def get_text_bounds(device_id, text_to_find, retries=3, delay=1):
    """
    連接到裝置後，尋找指定文字，並回傳它的 bounds。
    如果沒找到，會連續重試指定次數，每次停頓 delay 秒。
    
    :param device_id: 裝置ID
    :param text_to_find: 要查找的文字
    :param retries: 找不到時重試次數，預設3次
    :param delay: 每次重試的間隔秒數，預設1秒
    :return: bounds 字串或 None
    """
    d = u2.connect(device_id)
    
    for attempt in range(1, retries + 1):
        el = d.xpath(f'//*[@text="{text_to_find}"]').get()
        
        if el:
            bounds = el.attrib.get('bounds')
            return bounds
        else:
            if attempt < retries:
                print(f"文字 '{text_to_find}' 未找到，等待 {delay} 秒後重試 ({attempt}/{retries})...")
                time.sleep(delay)
            else:
                print(f"文字 '{text_to_find}' 未找到，已達最大重試次數 ({retries})")
    
    return None

def Key_Return():
    try:
        subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "4"], check=True)
  
        print("Key_Return")
    except Exception as e:
        print(f"Key_Return 錯誤")

def click_action(d, x, y, action="click", duration=0.1):
    """
    action: "click" (點擊), "long_click" (長按)
    duration: 按壓時間
    """
    if action == "long_click":
        print(f"⏳ 長按座標: ({x}, {y})")
        d.long_click(x, y, duration)
    else:
        print(f"🎯 點擊座標: ({x}, {y})")
        d.click(x, y)
   
def find_element_by_text(device_id, target_text):
    d = u2.connect(device_id)

    for el in d.xpath('//*').all():
        text = el.text
        bounds = el.attrib.get('bounds')
        if str(text).find(target_text) > -1:
            print("中了")
        if text and target_text in text:
            return el   # 找到就回傳元件

    return None  # 沒找到

if __name__ == '__main__':

  deviceid = "46081JEKB10015"
  device, client = connect(deviceid)
  device_id = device.serial
  point = 0
  #目前按鈕特性 是給 google pixel 8a用
  # 

  #收款帳號

  #text_to_input = '008'  # 輸入的文字 #華南銀行
  #text_to_input = '700'  # 輸入的文字 #郵局
  text_to_input = '007'  # 輸入的文字 #第一銀行
  #text_to_input = '004'  # 輸入的文字 #台灣銀行
  #text_to_input = '017'  # 輸入的文字 #兆豐

  #PhoneNumber = "0926865002"
  PhoneNumber = "0972461422"
  
  #匯款帳號
  #BankPoint = "582 1191" #台灣銀行
  #BankPoint = "582 1937" #第一銀行(1)
  #BankPoint = "582 1729" #第一銀行(2)
  #BankPoint = "582 2151" #華南
  BankPoint = "582 1485" #郵局
 
  #次數
  ForCount = 5

  d = u2.connect(device_id)

  step = 0

  print("正在獲取螢幕物件配置...")
  for i in range(99999999):
      try:

          if ForCount < 1 :
              print("結束")
              break;
          os.system('cls')   # Windows
          # 連接手機 (如果只有一台手機，通常不用填 serial
          print("---Start---------...")
          time.sleep(1.0)
          allspace = True
          d = u2.connect(device_id)
          time.sleep(1.0)


          for el in d.xpath('//*').all():
            # 檢查是否有文字 (使用 .text 屬性)
            text = el.text
            if text:
                # 獲取座標 (attrib 裡面的 bounds)
                bounds = el.attrib.get('bounds')
                # 獲取類別
                classname = el.attrib.get('class')
        
                print(f"內容: {text}")
                print(f"位置: {bounds}")
                print(f"類型: {classname}")

                if text.strip() == "轉帳" and step == 0:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 1
                    break
                if text.strip() == "手機門號" and step == 1:
                    #滑動
                    swipe_start = '500 100'
                    swipe_end = '500 0'
                    swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置

                    time.sleep(1.0)
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 2
                    break
                if text.strip() == "銀行 (搜尋並點選轉入銀行)" and step == 2:
                    # click_bounds(d, bounds)
                    nums = re.findall(r'\d+', bounds)
                    if len(nums) == 4:
                        left, top, right, bottom = map(int, nums)
                        # 計算中心點
                        center_x = (left + right) // 2
                        center_y = (top + bottom) // 2

                    dropdown_position = str(center_x) + ' ' + str(center_y)  # 下拉清單的位置
                    option_position = str(center_x) + ' ' + str(center_y + 100)    # 選擇的選項的位置
                    select_from_dropdown(device, dropdown_position,text_to_input, option_position)

                    time.sleep(1.0)
                    step = 3
                    break
                if text.strip() == "門號, 請確認輸入的帳號內容" and step == 3:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    input_characters(device, PhoneNumber)
                    time.sleep(1.0)
                    step = 4
                    Key_Return()
                    break
                if text.strip() == "門號, 門號須已在銀行設定轉帳入帳功能" and step == 3:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    input_characters(device, PhoneNumber)
                    time.sleep(1.0)
                    step = 4
                    Key_Return()
                    break
                if text.strip() == "金額" and step == 4:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    input_characters(device, "666")
                    time.sleep(1.0)

                    #滑動
                    swipe_start = '500 1200'
                    swipe_end = '500 500'
                    swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
                    time.sleep(1.0)
      
                    swipe_start = '500 1200'
                    swipe_end = '500 500'
                    swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
                    time.sleep(1.0)

                    step = 5

                    break
                if text.strip() == "忘記卡片密碼？" and step == 5:
                    # click_bounds(d, bounds)
                    nums = re.findall(r'\d+', bounds)
                    if len(nums) == 4:
                        left, top, right, bottom = map(int, nums)
                        # 計算中心點
                        center_x = (left + right) // 2
                        center_y = (top + bottom) // 2

                   
                    option_position = str(center_x) + ' ' + str(center_y - 200)    # 選擇的選項的位置
                    tap(device, option_position) 
                    time.sleep(1.0)
                    tap(device, BankPoint) 
                    time.sleep(1.0)
                    step = 6
                    Key_Return()
                    break
                if text.strip() == "卡片密碼(非實體卡密碼), 請輸入6-12位數字" and step == 6:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    ele = find_element_by_text(device_id,"不用了，謝謝")     
                    if ele is not None :
                        bounds = ele.attrib.get('bounds')
                        click_bounds(d, bounds)
                        time.sleep(1.0)
                    input_characters(device, "9393695")
                    time.sleep(1.0)
                    step = 7
                    Key_Return()

                    break
               
                if text.strip() == "輸入驗證碼" and step == 7:
                   

                    nums = re.findall(r'\d+', bounds)
                    if len(nums) == 4:
                        left, top, right, bottom = map(int, nums)
                        # 計算中心點
                        center_x = (left + right) // 2
                        center_y = (top + bottom) // 2

                    start_point = (106, top)  # 起始坐標 (x, y)
                    end_point = (506, bottom)    # 結束坐標 (x, y)
                    img = capture_screenshot(device)
                    cropped_img = crop_image(img, start_point, end_point)
                    resulttext = ddddocr_image(cropped_img)

                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    input_characters(device, resulttext)
                    time.sleep(1.0)
                    step = 8
                    Key_Return()
                    break
                if text.strip() == "確認" and step == 8:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 9
                    break
                if text.strip() == "驗證碼有誤，請重新輸入" and step == 9:
                    #click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 10
                    break
                if text.strip() == "確認" and step == 9:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 11
                    break
                if text.strip() == "確認" and step == 10:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 11
                    break
                if text.strip() == "更新" and step == 11:
                    nums = re.findall(r'\d+', bounds)
                    if len(nums) == 4:
                        left, top, right, bottom = map(int, nums)
                        # 計算中心點
                        center_x = (left + right) // 2
                        center_y = (top + bottom) // 2
                    click_action(d, center_x + 70 , center_y)
                    #tap(device, (center_x + 70 , center_y))
                    time.sleep(1.0)
                    step = 7
                    break
                if text.strip().find("下一步") > -1 and step == 9:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 20
                    break
                if text.strip().find("確認轉出") > -1 and step == 20:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 21
                    break
                if text.strip().find("確認") > -1 and step == 21:
                    click_bounds(d, bounds)
                    time.sleep(1.0)
                    step = 0
                    ForCount=ForCount-1
                    break

            else:
                 # 獲取座標 (attrib 裡面的 bounds)
                bounds = el.attrib.get('bounds')
                # 獲取類別
                classname = el.attrib.get('class')

                print(f"內容: {text}")
                print(f"位置: {bounds}")
                print(f"類型: {classname}")

                # 嘗試列印出所有屬性看看
                print(el.attrib)
      except Exception as ex:
            # 正確寫法 1：直接印出完整錯誤（最常用）
            traceback.print_exc()
    
            # 正確寫法 2：將錯誤轉成字串（存入變數，方便寫入 Log）
            full_error = traceback.format_exc()
            print(f"完整錯誤資訊：\n{full_error}")

  #for _ in range(ForCount):
 

  #    bounds = get_text_bounds(device_id,"轉帳")
  #    click_bounds(d, bounds)
  #    time.sleep(2.0)
  
  
  #    #手機轉帳
  #    while True:

  #        start_point = (750, 310)  # 起始坐標 (x, y)
  #        end_point = (1000, 400)    # 結束坐標 (x, y)

  #        img = capture_screenshot(device)
  #        cropped_img = crop_image(img, start_point, end_point)
  #        #resulttext = pytesseract_image(cropped_img)
  #        resulttext2 = paddleocr_image(cropped_img)
  #        if "手機門号" in resulttext2:
  #          print("偵測到手機門號欄位，準備輸入")
  #          #滑動
  #          swipe_start = '500 100'
  #          swipe_end = '500 0'
  #          swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
  #          time.sleep(1.0)

  #          tap(device, "886 334")
  #          time.sleep(1.0)
  #          break
  #        else:
  #          print("尚未偵測到手機門號欄位，等待中...")
  #          time.sleep(1.0)

  #          #滑動
  #          swipe_start = '500 100'
  #          swipe_end = '500 0'
  #          swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
  #          time.sleep(1.0)


  #    #判斷
  #    start_point = (160, 994)  # 起始坐標 (x, y)
  #    end_point = (403, 1098)    # 結束坐標 (x, y)

  #    img = capture_screenshot(device)
  #    cropped_img = crop_image(img, start_point, end_point)
  #    resulttext = pytesseract_image(cropped_img)
  #    resulttext2 = paddleocr_image(cropped_img)

  #    if resulttext2.find("轉帐對象") > -1 or resulttext2.find("转對象") > -1 or resulttext2.find("悵對象") > -1 :
  #        print("依轉帳位置 來決定 按鈕的步驟")
  #        point = 0
  #    else:
  #        #判斷
  #        start_point = (160, 456)  # 起始坐標 (x, y)
  #        end_point = (403, 582)    # 結束坐標 (x, y)

  #        img = capture_screenshot(device)
  #        cropped_img = crop_image(img, start_point, end_point)
  #        resulttext = pytesseract_image(cropped_img)
  #        resulttext2 = paddleocr_image(cropped_img)
  #        if resulttext2.find("轉帐對象") > -1 or resulttext2.find("转對象") > -1 or resulttext2.find("悵對象") > -1 :
  #          print("依轉帳位置 來決定 按鈕的步驟")
  #          point = 2
  #        else:
  #            #判斷
  #            start_point = (160, 844)  # 起始坐標 (x, y)
  #            end_point = (403, 948)    # 結束坐標 (x, y)

  #            img = capture_screenshot(device)
  #            cropped_img = crop_image(img, start_point, end_point)
  #            resulttext = pytesseract_image(cropped_img)
  #            resulttext2 = paddleocr_image(cropped_img)
  #            if resulttext2.find("轉帐對象") > -1 or resulttext2.find("转對象") > -1 or resulttext2.find("悵對象") > -1 :
  #              print("依轉帳位置 來決定 按鈕的步驟")
  #              point = 2
  #            else:
  #              point = 1

  #     #滑動
  #    swipe_start = '500 500'
  #    swipe_end = '500 2000'
  #    swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
  #    time.sleep(1.0)

  #    if (point == 0):
  #      dropdown_position = '474 1200'  # 下拉清單的位置
  #      option_position = '454 1030'    # 選擇的選項的位置
  #    else:
  #      dropdown_position = '679 695'  # 下拉清單的位置
  #      option_position = '454 854'    # 選擇的選項的位置
      

  #    # 從下拉清單中選擇
  #    select_from_dropdown(device, dropdown_position,text_to_input, option_position)
  #    time.sleep(1.0)

  #    #輸入帳號
  #    #input_characters(device, "0926865002")
  #    #input_characters(device, "0972461422")
  #    input_characters(device, PhoneNumber)
  #    time.sleep(1.0)
  
  #    if (point == 0):
  #        #滑動
  #        swipe_start = '500 1300'
  #        swipe_end = '500 500'
  #        swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
  #        time.sleep(2.0)
  
  #    #金額
  #    if (point == 0):
  #      tap(device, "548 585")
  #    elif (point == 2):
  #      tap(device, "548 1044")
  #    else:
  #      #tap(device, "548 1063")
  #      tap(device, "232 1192")
  #    input_characters(device, "666")
  #    time.sleep(1.0)

  #    #滑動
  #    swipe_start = '500 1200'
  #    swipe_end = '500 500'
  #    swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
  #    time.sleep(1.0)
      
  #    swipe_start = '500 1200'
  #    swipe_end = '500 500'
  #    swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
  #    time.sleep(1.0)

  #    #選擇卡片
  #    if (point == 0):
  #      tap(device, "564 1066")
  #    elif (point == 2):
  #      tap(device, "564 1177")
  #    else:
  #      tap(device, "558 1066")
      
  #    time.sleep(1.0)
  #    tap(device, BankPoint) 
  #    #tap(device, "582 1191") #台灣銀行
  #    #tap(device, "582 1937") #第一銀行(1)
  #    #tap(device, "582 1729") #第一銀行(2)
  #    #tap(device, "582 2151") #華南
  #    #tap(device, "582 1485") #郵局
  #    time.sleep(1.0)
  
  
  #    #輸入密碼
  #    if (point == 2):
  #      tap(device, "387 1422")
  #    else:
  #      tap(device, "387 1372")
  #    input_characters(device, "9393695")
  

  #    start_point = (138, 1583)  # 起始坐標 (x, y)
  #    end_point = (429, 1750)    # 結束坐標 (x, y)
         
  #    img = capture_screenshot(device)
  #    cropped_img = crop_image(img, start_point, end_point)
  #    resulttext = ddddocr_image(cropped_img)

  #    #if check_error_code(resulttext, "1"):
  #    #取消輸入框
  #    tap(device, "270 2318")
  #    time.sleep(1.0)

 

      

  #    #tap(device, "270 2318")
  #    #time.sleep(1.0)
     
  #    while True:
  #        tap(device, "349 1726")
  #        time.sleep(1.0)
          
  #        #圖片驗證
  #        if (point == 2):
  #          start_point = (106, 1600)  # 起始坐標 (x, y)
  #          end_point = (506, 1750)    # 結束坐標 (x, y)
  #        else:
  #          start_point = (106, 1487)  # 起始坐標 (x, y)
  #          end_point = (506, 1689)    # 結束坐標 (x, y)
          

  #        img = capture_screenshot(device)
  #        cropped_img = crop_image(img, start_point, end_point)
  #        resulttext = ddddocr_image(cropped_img)
  #        if check_error_code(resulttext, "生活"):
  #          continue

  #        if (point == 2):
  #           tap(device, "684 1694")
  #        else:
  #           tap(device, "684 1614")

         
  #        time.sleep(1.0)
  #        tap(device, "953 1994")
  #        tap(device, "953 1994")
  #        tap(device, "953 1994")
  #        tap(device, "953 1994")
  #        tap(device, "953 1994")
  #        #輸入你的驗證碼
  #        input_characters(device, resulttext)
  #        time.sleep(1.0)
  
  #        tap(device, "943 2145")
  #        time.sleep(1.0)
  
    
  #        #確認
  #        tap(device, "492 2150")
  #        time.sleep(4.0)
  
  #        #確認
  #        tap(device, "492 2150")
  #        time.sleep(1.0)
          
  #        #錯誤視窗判斷
  #        start_point = (103, 940)  # 起始坐標 (x, y)
  #        end_point = (1000, 1400)    # 結束坐標 (x, y)

  #        img = capture_screenshot(device)
  #        cropped_img = crop_image(img, start_point, end_point)
  #        resulttext = pytesseract_image(cropped_img)
  #        resulttext2 = paddleocr_image(cropped_img)


  #        error_code = '8101'
  #        if check_error_code(resulttext, error_code) or check_error_code(resulttext2, error_code):
  #          print(f"Error code {error_code} found in the image!")
  #          #確認
  #          tap(device, "855 1355")
  #          time.sleep(1.0)
            
  #          tap(device, "319 1788")
  #          time.sleep(1.0)

  #        elif check_error_code(resulttext,  '9999') or check_error_code(resulttext2, '9999'):
  #          print(f"Error code {error_code} found in the image!")
  #          #確認
  #          tap(device, "845 1276")
  #          #tap(device, "855 1355")
  #          time.sleep(1.0)
  #        elif check_error_code(resulttext,  '0601'):
  #          print(f"Error code {error_code} found in the image!")
  #          #確認
  #          tap(device, "845 1276")
  #          #tap(device, "855 1355")
  #          time.sleep(1.0)
  #        elif check_error_code(resulttext,  'NVERZARRAIEUR ') or check_error_code(resulttext,  'AB A Shh'):
  #          print(f"網路錯誤")
  #          #確認
  #          tap(device, "916 1324")
  #          #tap(device, "855 1355")
  #          time.sleep(1.0)
  #        elif check_error_code(resulttext,  'Boat ite Re') or check_error_code(resulttext,  'WATT SA 16S'):
  #          print(f"結束")
  #          #確認
  #          break
  #        elif check_error_code(resulttext,  'an eal A'):
  #          print(f"驗證碼 沒按到")
  #          tap(device, " 904 1261 ")
  #          time.sleep(1.0)

  #          tap(device, "684 1698")
  #          time.sleep(1.0)


  #          tap(device, "387 1462")
  #          input_characters(device, "9393695")
  #          time.sleep(1.0)

  #          tap(device, "270 2318")
  #          time.sleep(1.0)

  #          #確認
  #          #break
  #        elif check_error_code(resulttext,  'Hz ene AZ') or check_error_code(resulttext2,  '請輸入圖形證碼'):
  #          print(f"請輸入圖形驗證碼")
  #          tap(device, "919 1261 ")
  #          time.sleep(1.0)
          
           
       
  #        elif check_error_code(resulttext,  'TERRE') or check_error_code(resulttext2,  '請勿信指令操作付款'):
  #          print(f"結束")
  #          #確認
  #          break
  #        elif check_error_code(resulttext,  'ERENT') or check_error_code(resulttext,  'BBA SSR') or check_error_code(resulttext,  'RAR BE RATT'):
  #          print(f"結束")
  #          #確認
  #          break  
  #        elif check_error_code(resulttext,  'WARE RE AI FC HY') or check_error_code(resulttext2,  '警政署165') :
  #          print(f"結束")
  #          #確認
  #          break  
          
         
  #        else:
  #          print(f"Error code {error_code} not found in the image.")
  #          time.sleep(3.0)
  #          #break


  #    time.sleep(4.0)
  #    tap(device, "844 1500")
  #    time.sleep(4.0)
  #    print("結束-End-4")
  #    error_code = '9999'
  #    if check_error_code(resulttext, error_code):
  #      print(f"Error code {error_code} found in the image!")
  #      #確認
  #      tap(device, "845 1276")
  #      #tap(device, "855 1355")
  #      time.sleep(2.0)
       
  #    print("結束-End-3")
  #    # else:
  #    #   print(f"Error code {error_code} not found in the image.")
  #    #   time.sleep(3.0)
      
      

  #    tap(device, "847 1380")
  #    time.sleep(8.0)
  #    print("結束-End-2")
  #    tap(device, "321 2162")
  #    time.sleep(1.0)
  #    print("結束-End-1")
  #    #time.sleep(14.0)
  
  
  

    