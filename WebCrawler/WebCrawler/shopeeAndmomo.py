# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 12:23:27 2021

@author: dermo
"""

from asyncio.windows_events import NULL
import time
import pytesseract
from PIL import Image
import io
import os
import ddddocr
import re
import subprocess
from PIL import Image, ImageEnhance, ImageFilter
from ppadb.client import Client as AdbClient


ocr = ddddocr.DdddOcr()

momoflag = 0

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
    
def swipe_to_position(device, start, end, duration=1000):
    device.shell(f'input swipe {start} {end} {duration}')
    time.sleep(1)  # 等待滑动完成
    
def capture_screenshot(device):
    try:
        result = device.screencap()
        img = Image.open(io.BytesIO(result))
         # 保存到当前工作目录
        img.save(os.path.join(os.getcwd(), 'full_screen.png'))
    except subprocess.CalledProcessError as e:
        img = NULL
    return img

def crop_image(img, start_point, end_point):
    left, top = start_point
    right, bottom = end_point
    cropped_img = img.crop((left, top, right, bottom))
     # 保存到当前工作目录
    cropped_img.save(os.path.join(os.getcwd(), 'cropped_image.png'))
    return cropped_img

def ddddocr_image(img):
    try:
        image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
        result = ocr.classification(image, png_fix=True)
    except subprocess.CalledProcessError as e:
        result = NULL
    return result



def pytesseract_image(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
    result = pytesseract.image_to_string(img)
    return result

def pytesseract_image_Chitra(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image.png'))
    
    # 轉灰階
    gray_image = image.convert('L')
    # 增強對比度
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2.0)
    # 去噪
    filtered_image = enhanced_image.filter(ImageFilter.MedianFilter())
    
    result = pytesseract.image_to_string(filtered_image, lang='chi_tra')
    return result

def check_error_code(text, error_code):
    # 检查文本中是否包含指定的错误码
    if error_code in text:
        return True
    return False

def turn_off_screen():
    try:
        subprocess.run(["adb", "root"], check=True)
        
        # 禁用自動亮度調整
        subprocess.run(["adb", "shell", "settings", "put", "system", "screen_brightness_mode", "0"], check=True)
        
        # 將亮度設置為最低，接近關閉背光
        subprocess.run(["adb", "shell", "settings", "put", "system", "screen_brightness", "1"], check=True)


        print("螢幕已關閉")
    except subprocess.CalledProcessError as e:
        print(f"錯誤：{e}")
   
def turn_on_screen():
    try:
        subprocess.run(["adb", "root"], check=True)
        
        # 禁用自動亮度調整
        subprocess.run(["adb", "shell", "settings", "put", "system", "screen_brightness_mode", "0"], check=True)
    
        # 將亮度設置為最低，接近關閉背光
        subprocess.run(["adb", "shell", "settings", "put", "system", "screen_brightness", "70"], check=True)

  
        print("螢幕已開啟")
    except subprocess.CalledProcessError as e:
        print(f"錯誤：{e}")
   
def momo():
    #換momo
    tap(device, "884 1895 ")
    time.sleep(2.0)

    tap(device, "884 1895 ")
    time.sleep(2.0)
    momoflag = 0
    # #錯誤視窗判斷
    end = False
    for _ in range(10):
        start_point = (855, 396)  # 起始坐標 (x, y)
        end_point = (1016, 471)    # 結束坐標 (x, y)

        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = pytesseract_image(cropped_img)
      
        resulttext2 = ddddocr_image(cropped_img)
        if (re.search(r'\d', resulttext2)):
            end = False
            break
        else:
           
            tap(device, "873 614 ")
            time.sleep(6.0)
    
            tap(device, "250 1010 ")

            swipe_start = '500 1000 '
            swipe_end = '500 200 '
            swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
            time.sleep(2.0)

            
            
            momoflag = momoflag + 1
            
            end = True
       
        
    if end and momoflag >= 10:
           
        for _ in range(10):
            swipe_start = '500 200 '
            swipe_end = '500 1000 '
            swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
            time.sleep(2.0)
    
    #回蝦皮
    tap(device, "279 2319 ")
    time.sleep(2.0)
    
    tap(device, "778 916 ")
    time.sleep(2.0)

   
          
if __name__ == '__main__':

  device, client = connect()

  jump = 0
  momoflag = 0
  
  for _ in range(99999999):
      
      turn_on_screen()
      while True:
        try:
            start_point = (800, 300+jump)  # 起始坐標 (x, y)
            end_point = (1050, 350+jump)    # 結束坐標 (x, y)
      
            # 截圖並裁剪
            img = capture_screenshot(device)
            cropped_img = crop_image(img, start_point, end_point)

            # 執行 OCR
            #resulttext = pytesseract_image(cropped_img)
            resulttext2 = ddddocr_image(cropped_img)
           
           

            resulttext2 = resulttext2.replace("o","0")
            # 使用正則表達式替換
            resulttext2 = re.sub(r"[a-zA-Z]", "", resulttext2)

            filtered_text = re.sub(r'\D', '', resulttext2)
            # 確保有至少 4 位數字
            if resulttext2.find("已错束") > -1:
                jump = 400
                raise ValueError("已結束")

            #if len(filtered_text) == 3:
            #    filtered_text = "0" + filtered_text
            if len(filtered_text) < 4:
                raise ValueError("輸入字串長度不足 4 位數")
        
            # 嘗試提取並轉換前 4 個字元為數字
            time_str = filtered_text[:4]
            minutes = int(time_str[:2])
            seconds = int(time_str[2:])
        
            # 計算總秒數
            total_seconds = minutes * 60 + seconds
            if total_seconds > 600:
                raise ValueError("判斷秒數大於600 有問題")
            print(total_seconds)
            break  # 成功後跳出循環

           
        except ValueError as e:
            jump = jump + 5
            print(f"錯誤：{e}，重新嘗試...")
            if jump < 100 and jump > -300:
                jump = 110
            elif  jump < 200 and jump > 150 :
                jump = 220
           
                
            if  jump > 300:
                break


      if jump > 300:
          swipe_start = '500 1000 '
          swipe_end = '500 200 '
          swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
          time.sleep(1.0)
          jump = jump - 300
          continue 
      
      print("目前偵測圖片位置" + str(jump))
      
      #轉盤
      tap(device, "976 704 ")
      time.sleep(2.0)

      tap(device, "542 1058 ")
      time.sleep(3.0)

      tap(device, "754 1300 ")
      time.sleep(10.0)

      tap(device, "545 1481 ")
      time.sleep(2.0)
      
      tap(device, "545 1759 ")
      time.sleep(2.0)

      turn_off_screen()

      caltotal_seconds = total_seconds
      for _ in range(total_seconds):

        time.sleep(1)
        caltotal_seconds = caltotal_seconds -1
        print("還剩下" + str(caltotal_seconds) + "秒")
      turn_on_screen()
      
      # #錯誤視窗判斷
      start_point = (857, 407)  # 起始坐標 (x, y)
      end_point = (1007, 470)    # 結束坐標 (x, y)

      img = capture_screenshot(device)
      cropped_img = crop_image(img, start_point, end_point)
      resulttext = pytesseract_image(cropped_img)
      
      resulttext2 = ddddocr_image(cropped_img)

      tap(device, "250 1010 ")

      index = 301+jump
      tap(device, "984 " + str(index))
      time.sleep(3.0)
      
      index = 1473
      tap(device, "554 "+ str(index))
      time.sleep(3.0)
      
      tap(device, "250 1010 ")

      start_point = (900, 300+jump)  # 起始坐標 (x, y)
      end_point = (1050, 350+jump)    # 結束坐標 (x, y)
      
      # 截圖並裁剪
      img = capture_screenshot(device)
      cropped_img = crop_image(img, start_point, end_point)

      # 執行 OCR
      #resulttext = pytesseract_image(cropped_img)
      resulttext2 = ddddocr_image(cropped_img)
      resulttext2 = resulttext2.replace("o","0")
      # 使用正則表達式移除非數字字元
      filtered_text = re.sub(r'\D', '', resulttext2)

      
      # 確保有至少 4 位數字
      if len(filtered_text) == 4:
           print("可以繼續")
           #momo()
           #continue 
      else:
          swipe_start = '500 1000 '
          swipe_end = '500 200 '
          swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
          time.sleep(1.0)
          jump = jump - 300
       
      #轉盤
      tap(device, "976 704 ")
      time.sleep(2.0)

      tap(device, "542 1058 ")
      time.sleep(3.0)

      tap(device, "754 1300 ")
      time.sleep(10.0)

      tap(device, "545 1481 ")
      time.sleep(2.0)
      
      tap(device, "545 1759 ")
      time.sleep(2.0)



      momo()



      # #轉帳
      # #tap(device, "676 1281")
      # tap(device, "644 1610")
      # time.sleep(1.0)
  
      # #手機轉帳
      # tap(device, "886 334")
      # time.sleep(1.0)

      #  #滑動
      # swipe_start = '500 500'
      # swipe_end = '500 2000'
      # swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
      # time.sleep(1.0)

      # dropdown_position = '474 1200'  # 下拉清單的位置
      # text_to_input = '008'  # 輸入的文字 #華南銀行
      # #text_to_input = '700'  # 輸入的文字 #郵局
      # #text_to_input = '007'  # 輸入的文字 #第一銀行
      # option_position = '454 1030'    # 選擇的選項的位置

      # # 從下拉清單中選擇
      # select_from_dropdown(device, dropdown_position,text_to_input, option_position)
      # time.sleep(1.0)

      # #輸入帳號
      # input_characters(device, "0926865002")
      # time.sleep(1.0)
  
      # #滑動
      # swipe_start = '500 1300'
      # swipe_end = '500 500'
      # swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
      # time.sleep(2.0)
  
      # #金額
      # tap(device, "262 690")
      # input_characters(device, "666")
      # time.sleep(1.0)

      # #滑動
      # swipe_start = '500 1500'
      # swipe_end = '500 500'
      # swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
      # time.sleep(1.0)

      # #選擇卡片
      # tap(device, "558 1058")
      # time.sleep(1.0)
      # #tap(device, "582 1382") #第一銀行(1)
      # #tap(device, "582 1882") #第一銀行(2)
      # #tap(device, "582 1636") #華南
      # tap(device, "582 2125") #郵局
      # time.sleep(1.0)
  
  
      # #輸入密碼
      # tap(device, "387 1338")
      # input_characters(device, "9393695")
  
      # #取消輸入框
      # tap(device, "798 2198")
      # time.sleep(1.0)
      # tap(device, "824 2341")
      # time.sleep(1.0)

      # while True:
      #     #圖片驗證
      #     start_point = (117, 1524)  # 起始坐標 (x, y)
      #     end_point = (496, 1695)    # 結束坐標 (x, y)

      #     img = capture_screenshot(device)
      #     cropped_img = crop_image(img, start_point, end_point)
      #     resulttext = ddddocr_image(cropped_img)

      #     #輸入你的驗證碼
      #     input_characters(device, resulttext)
      #     time.sleep(1.0)
  
      #     #確認
      #     tap(device, "492 2150")
      #     time.sleep(1.0)
  

      #     #錯誤視窗判斷
      #     start_point = (103, 940)  # 起始坐標 (x, y)
      #     end_point = (715, 1400)    # 結束坐標 (x, y)

      #     img = capture_screenshot(device)
      #     cropped_img = crop_image(img, start_point, end_point)
      #     resulttext = pytesseract_image(cropped_img)
  
      #     error_code = '8101'
      #     if check_error_code(resulttext, error_code):
      #       print(f"Error code {error_code} found in the image!")
      #       #確認
      #       tap(device, "855 1355")
      #       time.sleep(1.0)
          
      #     else:
      #       print(f"Error code {error_code} not found in the image.")
      #       time.sleep(3.0)
      #       break



      # tap(device, "515 2160")
      # time.sleep(3.0)
  
      # error_code = '9999'
      # if check_error_code(resulttext, error_code):
      #   print(f"Error code {error_code} found in the image!")
      #   #確認
      #   tap(device, "882 1276")
      #   #tap(device, "855 1355")
      #   time.sleep(1.0)
          
      # # else:
      # #   print(f"Error code {error_code} not found in the image.")
      # #   time.sleep(3.0)
      
      

      # tap(device, "847 1380")
      # time.sleep(3.0)
  
      # tap(device, "321 2162")
      # time.sleep(1.0)
  
  
  

    