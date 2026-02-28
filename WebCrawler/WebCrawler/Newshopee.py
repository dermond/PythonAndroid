# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 12:23:27 2021

@author: dermo
"""

import io
import os
import psutil
import time
import datetime
import pytesseract
from PIL import Image
import paddle
import ddddocr
import re
import subprocess
from PIL import Image, ImageEnhance, ImageFilter
from ppadb.client import Client as AdbClient
#from datetime import datetime
import gc
import sys
from paddleocr import PaddleOCR #paddlepaddle
import subprocess
import re
import cv2
import Service.SettingReader as SettingReader
import threading
import socket
import struct


TotalCount = 0
device_id = ''
deviceid = ''
ocr = ddddocr.DdddOcr()
Pocr = PaddleOCR(use_angle_cls=False, lang='ch')  # lang='ch' 支援
Leftspace = 0
jump = 0
BaseJump = 0
resolution_width = 0
resolution_height = 0
dpi = 10
ErrorCount = 0
nextsession = 0
last_date = datetime.date.today()
okflag = 0


# 基準解析度（你定點位用的那台）
BASE_WIDTH  = 1080
BASE_HEIGHT = 2400
BASE_DPI = 420

def check_garbage_objects():
    gc.collect()  # 手動觸發垃圾回收
    uncollected = gc.garbage
    print(f"[GC] 未回收對象數量：{len(uncollected)}")
    
def print_memory_usage():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024 / 1024  # 單位 MB
    print(f"[記憶體使用量]：{mem:.2f} MB")
    
def connect(serial: str):
    client = AdbClient(host='127.0.0.1', port=5037)

    try:
        devices = client.devices()
    except Exception as e:
        if e.args[0].find("Is adb running on your computer?") > -1 :
            subprocess.run(["adb", "start-server"])
            devices = client.devices()
    if not devices:
        print('No devices')
        sys.exit()

    # 嘗試找出符合 serial 的裝置
    for device in devices:
        print(str(device.serial))
        if device.serial == serial:
            print(f'Connected to {device}')
            return device, client

    # 找不到時回傳第一筆裝置
    if serial == "":
        fallback_device = devices[0]
        print(f'Device with serial "{serial}" not found, fallback to {fallback_device.serial}')
        #quit()
    else:
        sys.exit()
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

# def capture_screenshot(device=None, local_filename='full_screen.png'):
#     remote_path = "/sdcard/screen.png"

#     try:
#         # 使用 adb shell screencap 指令截圖
        #os.system(f"adb shell screencap -p {remote_path}")
#         time.sleep(0.5)  # 確保檔案生成完成

#         # 將圖片從設備拉回本地
#         os.system(f"adb pull {remote_path} {local_filename}")

#         # 刪除設備端檔案（可選）
#         os.system(f"adb shell rm {remote_path}")

#         # 開啟並回傳圖片物件
#         img = Image.open(local_filename)
        
#         img.save(os.path.join(os.getcwd(), 'full_screen.png'))
        
#         return img

#     except Exception as e:
#         print(f"截圖失敗：{e}")
#         return None
    
def adb_init(device_id):

  
    # 1. 重新啟動 ADB（避免長時間卡死）
    subprocess.run(["adb", "kill-server"])
    time.sleep(2.0)
    subprocess.run(["adb", "start-server"])
    time.sleep(2.0)
    # 2. 重新連線裝置
    subprocess.run(["adb", "-s", device_id, "wait-for-device"])

    # 3. 讓手機永遠不睡眠
    subprocess.run([
        "adb", "-s", device_id, 
        "shell", "settings", "put", "global", "stay_on_while_plugged_in", "3"
    ])

    # 4. 關閉 Doze（避免 framebuffer / GPU 停止渲染）
    subprocess.run([
        "adb", "-s", device_id,
        "shell", "dumpsys", "deviceidle", "disable"
    ])

    # 5. 防止 USB 進入省電模式
    subprocess.run([
        "adb", "-s", device_id,
        "shell", "svc", "usb", "setFunctions", "mtp"
    ])

    # 6. 再執行 root（若裝置支援）
    try:
        subprocess.run(["adb", "-s", device_id, "root"], check=True)
    except:
        print("裝置不支援 adb root，忽略")

    print(f"{device_id} 初始化完成，可開始穩定截圖。")

    subprocess.run(["adb", "-s", device_id, "shell", "killall", "surfaceflinger"])
    time.sleep(2)

    #subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "26"])  # 電源鍵
    #time.sleep(1)
    #subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "3"])   # Home
    subprocess.run([
        "adb", "-s", device_id, 
        "shell", "wm", "size", f"{resolution_width}x{resolution_height}"
    ])
    time.sleep(1)
    subprocess.run(["adb", "-s", device_id, "shell", "wm", "size", "reset"])

def capture_screenshot(device):
    try:
        result = device.screencap()
        img = Image.open(io.BytesIO(result))
         # 保存到当前工作目录
        img.save(os.path.join(os.getcwd(), 'full_screen_'+str(deviceid)+'.png'))

     
    except:
        img = None 
    return img

def is_black_image(threshold=10):
    import numpy as np
    """
    threshold = 平均亮度低於多少視為黑畫面（0~255）
    """
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image_'+str(deviceid)+'.png')).convert("L")  # 轉灰階
    arr = np.array(image)
    mean_brightness = arr.mean()
    return mean_brightness < threshold
def crop_image(img, start_point, end_point):
    try:
        image2 = Image.open(os.path.join(os.getcwd(), 'full_screen_'+str(deviceid)+'.png')).convert("RGB")
         
        left, top = start_point
        right, bottom = end_point
        cropped_img = image2.crop((left, top, right, bottom))
         # 保存到当前工作目录
        cropped_img.save(os.path.join(os.getcwd(), 'cropped_image_'+str(deviceid)+'.png'))

        # 判斷是否黑畫面
        if is_black_image():
            print("⚠️  偵測到黑畫面！開始修復...")
            adb_recover(device_id)
            # 修好後重新建立 device 連線
            d = adbutils.adb.device(device_id)

    except Exception as e:
        cropped_img = None
    return cropped_img

def ddddocr_image(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image_'+str(deviceid)+'.png')).convert("RGB")
    result = ocr.classification(image, png_fix=True)

    return result



def pytesseract_image(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image_'+str(deviceid)+'.png')).convert("RGB")
    if img == None:
        return ""
    result = pytesseract.image_to_string(img)
    return result

def pytesseract_image_Chitra(img):
    image = Image.open(os.path.join(os.getcwd(), 'cropped_image_'+str(deviceid)+'.png')).convert("RGB")
    
    # 轉灰階
    gray_image = image.convert('L')
    # 增強對比度
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2.0)
    # 去噪
    filtered_image = enhanced_image.filter(ImageFilter.MedianFilter())
    
    result = pytesseract.image_to_string(filtered_image, lang='chi_tra')
    return result

def paddleocr_image(img_path):
    full_path = os.path.join(os.getcwd(),  'cropped_image_'+str(deviceid)+'.png')
    results = Pocr.ocr(full_path)
    # 組合所有辨識到的文字
    text = '\n'.join([ line[1][0] for block in results for line in block ])
    return text

def check_error_code(text, error_code):
    # 检查文本中是否包含指定的错误码
    if error_code in text:
        return True
    return False

def turn_off_screen():
    try:
        subprocess.run(["adb", "-s", device_id, "root"], check=True)
        
        # 禁用自動亮度調整
        subprocess.run(["adb", "-s", device_id, "shell", "settings", "put", "system", "screen_brightness_mode", "0"], check=True)
        
        # 將亮度設置為最低，接近關閉背光
        subprocess.run(["adb", "-s", device_id, "shell", "settings", "put", "system", "screen_brightness", "1"], check=True)


        print("螢幕已關閉")
    except Exception as e:
        print(f"錯誤")
   
def turn_on_screen():
    try:
        subprocess.run(["adb", "-s", device_id, "root"], check=True)
        
        # 禁用自動亮度調整
        subprocess.run(["adb", "-s", device_id, "shell", "settings", "put", "system", "screen_brightness_mode", "0"], check=True)
    
        # 將亮度設置為最低，接近關閉背光
        subprocess.run(["adb", "-s", device_id, "shell", "settings", "put", "system", "screen_brightness", "1"], check=True)

  
        print("螢幕已開啟")
    except Exception as e:
        print(f"錯誤")
def Key_Return():
    try:
        subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "4"], check=True)
  
        print("Key_Return")
    except Exception as e:
        print(f"Key_Return 錯誤")
        
  
def log(message):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")
       
def validate_block(block):
    float_value = None
    time_value = None
    
    for item in block:
        # 嘗試匹配 0~5 的浮點數（最多 5.000...，不超過5）
        if re.fullmatch(r'0*(?:[0-4](?:\.\d+)?|5(?:\.0*)?)', item):
            float_value = float(item)

        # 嘗試匹配時間格式（mm:ss 或 hh:mm）
        if re.fullmatch(r'\d{1,2}:\d{2}', item):
            time_value = item

    # 同時具備浮點數 + 時間 才視為有效
    if float_value is not None and time_value is not None:
        return True, float_value, time_value
    else:
        return False, None, None

def run_adb_command(cmd):
    try:
        result = subprocess.run(['adb', 'shell'] + cmd.split(), capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"[錯誤] 無法執行 ADB：{e}")
        return ""

def get_screen_info_from_device(device):
   
    """
   
    傳入已連接的 ADB device 實體，回傳解析度與密度。
    回傳值：
      - resolution: (width, height)
      - density: dpi
      - display_info: 從 dumpsys display 中解析出的 width, height, densityDpi
    """
    global resolution_width
    global resolution_height
    
    # 取得解析度
    wm_size_output = device.shell("wm size")
    match_size = re.search(r'(Override|Physical) size:\s*(\d+)x(\d+)', wm_size_output)
    resolution = (int(match_size.group(2)), int(match_size.group(3))) if match_size else None
    resolution_width = int(match_size.group(2))
    resolution_height = int(match_size.group(3))
    # 取得密度
    wm_density_output = device.shell("wm density")
    match_density = re.search(r'(Override|Physical) density:\s*(\d+)', wm_density_output)
    density = int(match_density.group(2)) if match_density else None

    # 從 dumpsys display 擷取更多資訊
    dumpsys_display = device.shell("dumpsys display")
    match_display_info = re.search(
        r'DisplayDeviceInfo\{.*?width=(\d+), height=(\d+).*?densityDpi=(\d+)',
        dumpsys_display,
        re.DOTALL
    )
    if match_display_info:
        display_width = int(match_display_info.group(1))
        display_height = int(match_display_info.group(2))
        display_density_dpi = int(match_display_info.group(3))
        display_info = {
            "width": display_width,
            "height": display_height,
            "densityDpi": display_density_dpi
        }
    else:
        display_info = None

    return resolution, density, display_info

def convert_xy_with_dpi(x_base, y_base):
    """
    將基準裝置 (1080x2400, 420dpi) 上量到的 UI 點位
    轉換為目前裝置上的實際 tap 座標
    """
    # 1️⃣ px → dp（抽象成 UI 單位）
    dp_x = x_base * 160 / BASE_DPI
    dp_y = y_base * 160 / BASE_DPI

    # 2️⃣ dp → 基準 px（標準化）
    norm_x = dp_x * BASE_DPI / 160
    norm_y = dp_y * BASE_DPI / 160
    # ↑ 這一步其實等於回到 x_base / y_base
    #   目的是讓你看清「dpi 不該單獨決定位置」

    # 3️⃣ 依解析度比例調整位置
    x_target = int(norm_x / BASE_WIDTH  * resolution_width)
    y_target = int(norm_y / BASE_HEIGHT * resolution_height)

    return x_target, y_target

def calculate_x(y):
    #2400,1483
    #2560,1774
    return round(1.81875 * y - 2882)

def calculate_x2(y):
    #2400,1592
    #2560,1846
    return round(1.5875 * y - 2218)

def ReLoadShopee():
    # 關閉 Shopee
    device.shell(f"am force-stop {package_name}")
    print("Shopee 已停止")
    time.sleep(4.0)
    # 啟動 Shopee
    start_command = f"am start -n {package_name}/{activity_name}"
    output = device.shell(start_command)
    print(f"Shopee 已啟動，輸出：\n{output}")
    time.sleep(6.0)
        
    tap(device, str((resolution_width / 2) + 50) + " " + str((resolution_height) - 150))
    #tap(device, "545 2180 ")
    time.sleep(4.0)
    
    if resolution_width == 1080 and resolution_height == 2280 and density == 420:#deviceid == "R58N10RXWVF":
        tap(device, "600 203 ")
        time.sleep(2.0)
    elif resolution_width == 1080 and resolution_height == 2400 and density == 420  : #deviceid == "46081JEKB10015"
        tap(device, "600 203 ")
        time.sleep(2.0)

    elif resolution_width == 1440 and resolution_height == 2560 and density == 640: #deviceid == "FA75V1802306": (1440, 2560)
        tap(device, "825 220 ")
        time.sleep(2.0)
    elif resolution_width == 1080 and resolution_height == 2400 and density == 480 : #(1080, 2400)  de824891  :
        tap(device, "620 170 ")
        time.sleep(2.0)
    else:
        tap(device, "600 203 ")
        time.sleep(2.0)

def Nextshow(temp):
    global nextsession
    #重啟Shopee
    ReLoadShopee()
    #按下 直播
    if resolution_width == 1080 and resolution_height == 2280 and density == 420:#deviceid == "R58N10RXWVF":
        tap(device, "500 203 ")
        time.sleep(2.0)
    elif resolution_width == 1080 and resolution_height == 2400 and density == 420  : #deviceid == "46081JEKB10015"
        tap(device, "500 203 ")
        time.sleep(2.0)

    elif resolution_width == 1440 and resolution_height == 2560 and density == 640: #deviceid == "FA75V1802306": (1440, 2560)
        tap(device, "585 220 ")
        time.sleep(2.0)
        
        tap(device, "585 820 ")
        time.sleep(2.0)
        
        start_point = (50, 300)  # 起始坐標 (x, y)
        end_point = (300, 600)    # 結束坐標 (x, y)
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = paddleocr_image(cropped_img)  
        if resulttext.find("下一場次") > -1 and nextsession == 0:

            tap(device, str("175") + " " + str("450"))
            time.sleep(3.0)
            if resolution_height > 2000:
                tap(device, str("1150") + " " + str("1600"))
                # index = (resolution_height / 2)  - 10
                # tap(device, str(resolution_width - 240) + " " + str(index))
                time.sleep(5.0)
        
                tap(device, str("1150") + " " + str("2515"))
                time.sleep(5.0)
            else:
                index = (resolution_height / 2)  - 80
                tap(device, str(resolution_width - 140) + " " + str(index))
                time.sleep(5.0)
        
                index = resolution_height  - 300
                tap(device, str(resolution_width - 140) + " " + str(index))
                time.sleep(5.0)

            Key_Return()
            nextsession = 1
    elif resolution_width == 1080 and resolution_height == 2400 and density == 480 : #(1080, 2400)  de824891  :
        tap(device, "445 195 ")
        time.sleep(2.0)
        
        tap(device, "445 780 ")
        time.sleep(2.0)
        
        start_point = (0, 300)  # 起始坐標 (x, y)
        end_point = (200, 500)    # 結束坐標 (x, y)
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = paddleocr_image(cropped_img)  
        if resulttext.find("下一場次") > -1 and nextsession == 0:

            tap(device, str("175") + " " + str("450"))
            time.sleep(3.0)
            if resolution_height > 2000:
                tap(device, str("1150") + " " + str("1600"))
                # index = (resolution_height / 2)  - 10
                # tap(device, str(resolution_width - 240) + " " + str(index))
                time.sleep(5.0)
        
                tap(device, str("1150") + " " + str("2515"))
                time.sleep(5.0)
            else:
                index = (resolution_height / 2)  - 80
                tap(device, str(resolution_width - 140) + " " + str(index))
                time.sleep(5.0)
        
                index = resolution_height  - 300
                tap(device, str(resolution_width - 140) + " " + str(index))
                time.sleep(5.0)

            Key_Return()
            nextsession = 1
    else:
        tap(device, "500 203 ")
        time.sleep(2.0)


    

   
    
    for i in range(10):
        #往下一筆 短影音
        swipe_start = '500 1300'
        swipe_end = '500 100'
        swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
        time.sleep(8.0)

def judgment(temp):
    global jump
    global resolution_width
    global resolution_height
    global dpi
    global ErrorCount
    global TotalCount
    global LimitTotalCount
    global BaseJump
    global nextsession

    # 截圖並裁剪 A20 存取手機
    if resolution_width == 1080 and resolution_height == 2280 and density == 420:#deviceid == "R58N10RXWVF":
        start_point = (475, 1350)  # 起始坐標 (x, y)
        end_point = (594, 1410)    # 結束坐標 (x, y)
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = paddleocr_image(cropped_img)    
        if resulttext.find("允許")  > -1 :
            tap(device, str(534) + " " + str(1380))
            
        # 截圖並裁剪 偵測X 去按下
        if resolution_width == 720 and resolution_height == 1560:
            start_point = (250, 1300)  # 起始坐標 (x, y)
            end_point = (350, 1450)    # 結束坐標 (x, y)
        else:
            start_point = (480, 1780)  # 起始坐標 (x, y)
            end_point = (640, 1900)    # 結束坐標 (x, y)

        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = ddddocr_image(cropped_img)  
        #resulttext2 = pytesseract_image_Chitra(cropped_img)  
        if resulttext.find("x") > -1 or resulttext.find("大") > -1 or resulttext.find("十") > -1:
            index = 1800 
            tap(device, str(resolution_width / 2) + " " + str(index))

        # 截圖並裁剪 偵測X 去按下
        if resolution_width == 720 and resolution_height == 1560:
            start_point = (250, 1300)  # 起始坐標 (x, y)
            end_point = (350, 1450)    # 結束坐標 (x, y)
        else:
            start_point = (480, 1730)  # 起始坐標 (x, y)
            end_point = (640, 1850)    # 結束坐標 (x, y)


        # 截圖並裁剪
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = ddddocr_image(cropped_img)  
        #resulttext2 = pytesseract_image_Chitra(cropped_img)  
        if resulttext.find("x") > -1 or resulttext.find("大") > -1 or resulttext.find("十") > -1:
            index = 1800 
            tap(device, str(resolution_width / 2) + " " + str(index))
            
   
    elif resolution_width == 1080 and resolution_height == 2400 and density == 420  : #deviceid == "46081JEKB10015"
        start_point = (380, 1500)  # 起始坐標 (x, y)
        end_point = (740, 1650)    # 結束坐標 (x, y)
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = paddleocr_image(cropped_img)    
        if resulttext.find("簽到")  > -1 or resulttext.find("立即到")  > -1 or resulttext.find("立即")  > -1:
            tap(device, str(560) + " " + str(1575 ))        
    # 截圖並裁剪 HTC手機 無法充電的提示
    elif resolution_width == 1440 and resolution_height == 2560 and density == 640: #deviceid == "FA75V1802306": (1440, 2560)
        start_point = (1050, 1550)  # 起始坐標 (x, y)
        end_point = (1300, 1700)    # 結束坐標 (x, y)
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = paddleocr_image(cropped_img)    
        if resulttext.find("確定")  > -1 :
            tap(device, str(1175) + " " + str(1625))
            
        start_point = (530, 1780)  # 起始坐標 (x, y)
        end_point = (930, 1980)    # 結束坐標 (x, y)
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = paddleocr_image(cropped_img)    
        if resulttext.find("簽到")  > -1 or resulttext.find("立即到")  > -1 or resulttext.find("打開到")  > -1:
            tap(device, str(734) + " " + str(1880 ))        
        
   
    # 截圖並裁剪 VIVO手機 無法充電的提示
    elif resolution_width == 1080 and resolution_height == 2400 and density == 480 : #(1080, 2400)  de824891  :
        start_point = (380, 2080)  # 起始坐標 (x, y)
        end_point = (750, 2250)    # 結束坐標 (x, y)
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = paddleocr_image(cropped_img)    
        if resulttext.find("確定")  > -1 :
            tap(device, str(565) + " " + str(2165))
            
        # 截圖並裁剪 偵測X 去按下
        if resolution_width == 720 and resolution_height == 1560:
            start_point = (250, 1300)  # 起始坐標 (x, y)
            end_point = (350, 1450)    # 結束坐標 (x, y)
        else:
            start_point = (480, 1780)  # 起始坐標 (x, y)
            end_point = (640, 1900)    # 結束坐標 (x, y)

        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = ddddocr_image(cropped_img)  
        #resulttext2 = pytesseract_image_Chitra(cropped_img)  
        if resulttext.find("x") > -1 or resulttext.find("大") > -1 or resulttext.find("十") > -1:
            index = 1800 
            tap(device, str(resolution_width / 2) + " " + str(index))

        # 截圖並裁剪 偵測X 去按下
        if resolution_width == 720 and resolution_height == 1560:
            start_point = (250, 1300)  # 起始坐標 (x, y)
            end_point = (350, 1450)    # 結束坐標 (x, y)
        else:
            start_point = (480, 1730)  # 起始坐標 (x, y)
            end_point = (640, 1850)    # 結束坐標 (x, y)


        # 截圖並裁剪
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = ddddocr_image(cropped_img)  
        #resulttext2 = pytesseract_image_Chitra(cropped_img)  
        if resulttext.find("x") > -1 or resulttext.find("大") > -1 or resulttext.find("十") > -1:
            index = 1800 
            tap(device, str(resolution_width / 2) + " " + str(index))
    else:
        # 截圖並裁剪 偵測X 去按下
        if resolution_width == 720 and resolution_height == 1560:
            start_point = (250, 1300)  # 起始坐標 (x, y)
            end_point = (350, 1450)    # 結束坐標 (x, y)
        else:
            start_point = (480, 1780)  # 起始坐標 (x, y)
            end_point = (640, 1900)    # 結束坐標 (x, y)

        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = ddddocr_image(cropped_img)  
        #resulttext2 = pytesseract_image_Chitra(cropped_img)  
        if resulttext.find("x") > -1 or resulttext.find("大") > -1 or resulttext.find("十") > -1:
            index = 1800 
            tap(device, str(resolution_width / 2) + " " + str(index))

        # 截圖並裁剪 偵測X 去按下
        if resolution_width == 720 and resolution_height == 1560:
            start_point = (250, 1300)  # 起始坐標 (x, y)
            end_point = (350, 1450)    # 結束坐標 (x, y)
        else:
            start_point = (480, 1730)  # 起始坐標 (x, y)
            end_point = (640, 1850)    # 結束坐標 (x, y)


        # 截圖並裁剪
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext = ddddocr_image(cropped_img)  
        #resulttext2 = pytesseract_image_Chitra(cropped_img)  
        if resulttext.find("x") > -1 or resulttext.find("大") > -1 or resulttext.find("十") > -1:
            index = 1800 
            tap(device, str(resolution_width / 2) + " " + str(index))
            
   


    # start_point = (262, 800)  # 起始坐標 (x, y)
    # end_point = (880, 1350)    # 結束坐標 (x, y)
      
    # # 截圖並裁剪
    # img = capture_screenshot(device)
    # cropped_img = crop_image(img, start_point, end_point)
    # resulttext = paddleocr_image(cropped_img)  
    # if resulttext.find("紅包雨")  > -1:
    #     tap(device, str((resolution_width / 2)) + " " + str(calculate_x(resolution_height)))
    
    # if resulttext.find("您已觀看達30秒")  > -1:
    #     tap(device, str((resolution_width / 2)) + " " + str(calculate_x2(resolution_height)))
    # elif resulttext.find("第3天")  > -1:
    #     tap(device, str((resolution_width / 2)) + " " + str(calculate_x2(resolution_height)))
    

    #判斷數值
    if resolution_width == 720 and resolution_height == 1560:
        start_point = (600+ Leftspace, 100)  # 起始坐標 (x, y)
        end_point = (700+ Leftspace, 1050)    # 結束坐標 (x, y)
    else:
        start_point = (900+ Leftspace, 300)  # 起始坐標 (x, y)
        end_point = (1050+ Leftspace, 1350)    # 結束坐標 (x, y)

    # 截圖並裁剪
    img = capture_screenshot(device)
    cropped_img = crop_image(img, start_point, end_point)
    resulttext = paddleocr_image(cropped_img)  

    if resulttext.find("領取")  > -1 or resulttext.find("领取")  > -1 :
        turn_on_screen()
       
        if resolution_width == 720 and resolution_height == 1560:
            start_point = (600+ Leftspace, 100+jump)  # 起始坐標 (x, y)
            end_point = (700+ Leftspace, 200+jump)    # 結束坐標 (x, y)
        else:
            start_point = (800+ Leftspace, 280+jump)  # 起始坐標 (x, y)
            end_point = (1050+ Leftspace, 420+jump)    # 結束坐標 (x, y)

        print("比對领取" + " " + str(jump))
        
        # 截圖並裁剪
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)
        resulttext2 = paddleocr_image(cropped_img)  
        
        if resulttext2.find("領取")  > -1 or resulttext2.find("领取")  > -1 :
           
            print("第2次比對")
            if (jump > 100):
                BaseJump = 50
            
            elif (jump > 200):
                BaseJump = 100
            else:
                BaseJump = 0
        else:
            jump = jump + dpi
                    
            if jump > 650:
                return "next"
            
            return "wait"
            


        index = 321+jump 
        if resolution_width == 720 and resolution_height == 1560:
            index = 165+jump
            tap(device, str(650) + " " + str(index))
        else:
            tap(device, str(resolution_width - 106) + " " + str(index))
        time.sleep(4.0)
        if resolution_width == 720 and resolution_height == 1560:
            index = 935 
            tap(device, str(365) + " " + str(index))
        elif (resolution_height < 2400):
            index = 1360 
            tap(device, str(542) + " " + str(index))
        else:
            index = 1400 + (abs(2380 - resolution_height) * 2)
            tap(device, str(resolution_width / 2) + " " + str(index))
         
            

        time.sleep(4.0)
            
        TotalCount = int(TotalCount) + 1
        SettingReader.setSetting("base",deviceid + "TotalCount", str(TotalCount) )
        #判斷 下方位置是否有參加 可以按
        start_point = (900+ Leftspace, 450+jump)  # 起始坐標 (x, y)
        end_point = (1150+ Leftspace, 590+jump)    # 結束坐標 (x, y)
      
        # 截圖並裁剪
        img = capture_screenshot(device)
        cropped_img = crop_image(img, start_point, end_point)

        # 執行 OCR
        #resulttext = pytesseract_image(cropped_img)
        resulttext = paddleocr_image(cropped_img)  
        
        try:
        
            if resulttext.find("参加") > -1 and resulttext.find("已参加") == -1:
                #轉盤
                index = 520+jump

                tap(device, str(resolution_width  - 100) + " " + str(index) )
                time.sleep(4.0)

                start_point = (262, 800)  # 起始坐標 (x, y)
                end_point = (880, 1350)    # 結束坐標 (x, y)
      
                # 截圖並裁剪
                img = capture_screenshot(device)
                cropped_img = crop_image(img, start_point, end_point)
                resulttext = paddleocr_image(cropped_img) 
                  
                if resulttext.find("手機號碼") > -1:
                    index = (resolution_height / 2 ) + 100
                    tap(device, str(resolution_width / 4) + " " + str(index))
                    time.sleep(3.0)

               
                
                  
                index = (resolution_height / 2 ) - 100
                tap(device, str(resolution_width / 2) + " " + str(index))
                time.sleep(12.0)

                index = (resolution_height / 2 ) + 100
                tap(device, str((resolution_width / 2) + 200) + " " + str(index))
                time.sleep(12.0)

                index = (resolution_height / 2 ) + 282
                tap(device, str(resolution_width / 2) + " " + str(index))
                time.sleep(2.0)

        
        except ValueError:
       
            print("轉盤有錯誤")

        now = datetime.now().time()
        limit_time = time(23, 30)  # 23:30

        # ⛔ 還沒到 23:30
        if now < limit_time:
            return "ok"

        
        #if (device_id == "FA75V1802306"):
        #    tap(device, str(resolution_width - 106) + " " + str(index))
        #    time.sleep(3.0)
        #    index = 1732
        #    tap(device, "780 "+ str(index))
        #    time.sleep(3.0)
        #else:
        #    tap(device, str(984 + Leftspace) + " " + str(index))
        #    time.sleep(4.0)
      
        #    index = 1473
        #    tap(device, str(554 + Leftspace) + " " + str(index))
        #    time.sleep(4.0)
        return "ok"
               
        
       
    
    spilt = resulttext.split('\n')
    valid, value, time2 = validate_block(spilt)
    if valid:
        print("數值：", value)
        print("時間：", time2)
        ErrorCount = 0
        
        # 將 MM:SS 轉換為「總分鐘」
        minutes, seconds = map(int, time2.split(":"))
        wait_minutes = minutes + seconds / 60.0
        wait_sec = int(wait_minutes * 60)
        # 計算每分鐘收益
        value_per_minute = value / wait_minutes

        # 設定門檻值（你可以調整這個值）
        threshold = 0.02857

        # 顯示資訊
        print(f"數值：{value}")
        print(f"時間：{time2}（約 {wait_minutes:.2f} 分鐘）")
        print(f"每分鐘收益：{value_per_minute:.4f}")

        # 判斷是否執行
        if value_per_minute >= threshold:
            print("✅ 值得執行！")
        else:
            print("❌ 不值得執行")
            return "next"
            
        if value_per_minute >= threshold:
            print("每分鐘收益 值得執行")
            
            if resolution_width == 720 and resolution_height == 1560:
                start_point = (600+ Leftspace, 100+jump)  # 起始坐標 (x, y)
                end_point = (700+ Leftspace, 200+jump)    # 結束坐標 (x, y)
            else:
                start_point = (800+ Leftspace, 280+jump)  # 起始坐標 (x, y)
                end_point = (1050+ Leftspace, 420+jump)    # 結束坐標 (x, y)

            print("比對领取" + " " + str(jump))
            # 截圖並裁剪
            img = capture_screenshot(device)
            cropped_img = crop_image(img, start_point, end_point)
            resulttext2 = paddleocr_image(cropped_img)  
            spilt = resulttext2.split('\n')
            valid, value, time2 = validate_block(spilt)
            if valid:
                print("找到數值或是時間")
                for _ in range(wait_sec):

                    time.sleep(1)
                    wait_sec = wait_sec -1
                    print("還剩下" + str(wait_sec) + "秒")

            else:
                jump = jump + dpi
                    
                if jump > 650:
                    return "next"


            return "wait"
        else:
            print("數值小於 0.2")

            return "next"
    else:
        print("解析蝦皮和時間錯誤")
        ErrorCount = ErrorCount + 1
        if (ErrorCount < 1):
            return "wait"
        else:
            return "next"
   

if __name__ == '__main__':
  
  goflag = 0

  deviceid = "46081JEKB10015"
  deviceid = "de824891"
  #deviceid = "46081JEKB10015"
  #deviceid = "CTLGAD3852600256"
  
  if len(sys.argv) > 1:
        print("你輸入的參數如下：")
        for i, arg in enumerate(sys.argv[1:], start=1):
            print(f"參數 {i}：{arg}")
        deviceid = str(sys.argv[1])
  else:
    print("沒有輸入任何參數")
  
 
  adb_init(deviceid)
  device, client = connect(deviceid)
  device_id = device.serial
  jump = 150
  BaseJump = 0
  Leftspace = 0
  dpi = 10

  #解析度（wm size）：(1080, 2400) 螢幕密度（wm density）：480 dpi de824891
  #解析度（wm size）：(1080, 2400) 螢幕密度（wm density）：420 dpi 46081JEKB10015
  #解析度（wm size）：(1440, 2560) 螢幕密度（wm density）：640 dpi FA75V1802306
  #解析度（wm size）：(1080, 2280) 螢幕密度（wm density）：420 dpi

  resolution, density, display_info = get_screen_info_from_device(device)

  print(f"解析度（wm size）：{resolution}")
  print(f"螢幕密度（wm density）：{density} dpi")
  if display_info:
    print(f"從 dumpsys display：{display_info['width']}x{display_info['height']}, {display_info['densityDpi']} dpi")
    

  
  if (resolution_width == 1440):
      Leftspace = 340
  if (density >= 640):
      dpi = 20

  if (resolution_height > 2000 and density == 640):
       jump = 300

  if (resolution_height > 2000 and density == 480):
       jump = 200
  # #錯誤視窗判斷
  # Shopee 的包名與主 Activity
  package_name = "com.shopee.tw"
  activity_name = "com.shopee.app.ui.home.HomeActivity_"
  
  Shopeecount = 0
  ErrorCount = 0
  
  LimitTotalCount = SettingReader.getSetting("base",deviceid + "LimitTotalCount")
  if LimitTotalCount == '':
      LimitTotalCount = 80
      SettingReader.setSetting("base",deviceid + "LimitTotalCount", LimitTotalCount )

  TotalCount = SettingReader.getSetting("base",deviceid + "TotalCount")
  if TotalCount == '':
      TotalCount = 0
      SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
  TotalCount = int(TotalCount)
  

  today = datetime.date.today()
  yesterday = today - datetime.timedelta(days=1)
  
  (xpoint,ypoint) =convert_xy_with_dpi(130,430);
  for i in range(99999999):
    try:

  
        current_date = str(datetime.date.today())
        getdate = SettingReader.getSetting("base",deviceid + "date")
    
        TotalCount = SettingReader.getSetting("base",deviceid + "TotalCount")
    
        # 如果是空字串，給預設值 0
        if TotalCount == "" or TotalCount is None:
            TotalCount = 0
            SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
    
        if getdate != current_date:
            TotalCount = 0
            SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
            SettingReader.setSetting("base",deviceid + "date", current_date )
            adb_init(deviceid)
        
        now = datetime.datetime.now().time()

        start_time = datetime.time(5, 0)    # 05:00
        end_time   = datetime.time(5, 30)   # 05:30

        # ✅ 只有在 05:00~05:30 之間
        if start_time <= now <= end_time:
            TotalCount = 0
            SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
            SettingReader.setSetting("base",deviceid + "date", current_date )
            adb_init(deviceid)

        check_garbage_objects()
        print_memory_usage()
        turn_off_screen()
        if Shopeecount > 10:  # 如果 i 是 10 的倍數
            print(f"第 {i} 次操作：重啟 Shopee App")
        
           
            ReLoadShopee()
            # tap(device, "740 190 ")
            # time.sleep(3.0)
        
            # tap(device, "322 1263 ")
            # time.sleep(1.0)
            Shopeecount = 0
        
        start_time = datetime.time(8, 0)    # 08:00
        end_time   = datetime.time(12, 00)   # 11:00
        # ✅ 只有在 08:00~11:00 之間
        if start_time <= now <= end_time:
            #進行
            Nextshow(0)


        now = datetime.datetime.now()
        now_time = now.time()
        weekday = now.weekday()  # 0 = 星期一, 6 = 星期日

        # 定義每天的禁止執行時間區段（start_time, end_time）
        restricted_times = {
            0: (datetime.time(1, 0), datetime.time(13, 0)),   # 星期一
            1: (datetime.time(1, 0), datetime.time(13, 0)),   # 星期二
            2: (datetime.time(1, 0), datetime.time(13, 0)),   # 星期三
            3: (datetime.time(1, 0), datetime.time(13, 0)),   # 星期四
            4: (datetime.time(1, 0), datetime.time(13, 0)),   # 星期五
            5: (datetime.time(1, 0), datetime.time(13, 0)),   # 星期六
            6: (datetime.time(1, 0), datetime.time(13, 0)),   # 星期日
        }

        start, end = restricted_times[weekday]

        # 判斷是否在禁止區段內（處理跨午夜的情況）
        in_restricted = False
        if start < end:
            # 時間區段沒有跨午夜
            in_restricted = start <= now_time < end
        else:
            # 時間區段跨午夜，例如 23:00 ~ 10:00
            in_restricted = now_time >= start or now_time < end

        if in_restricted:
            print(f"現在時間 {now_time} 在禁止區段 ({start}~{end})，跳過執行，時間：{now}")
            time.sleep(10.0)
        
            #滑動
            swipe_start = '500 1300'
            swipe_end = '500 500'
            swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
            time.sleep(2.0)

            if goflag == 0 :
                device.shell(f"am force-stop {package_name}")
                print("Shopee 已停止")
                time.sleep(2.0)
            
            goflag = 1
            nextsession = 0
            continue

        if goflag == 1 :
            # 啟動 Shopee
            start_command = f"am start -n {package_name}/{activity_name}"
            output = device.shell(start_command)
            print(f"Shopee 已啟動，輸出：\n{output}")
            time.sleep(4.0)
        
            tap(device, str((resolution_width / 2) + 50) + " " + str((resolution_height) - 200))
            #tap(device, "545 2180 ")
            time.sleep(2.0)
        goflag = 0

        # 如果不在禁止區段，就執行你的主程式
        print(f"現在時間 {now_time} 可以執行，時間：{now}")
    
        print(f"TotalCount：\n{str(TotalCount)}")
        if int(TotalCount) > int(LimitTotalCount):
            print(f"TotalCount 大於"+str(LimitTotalCount)+f"次：\n{str(TotalCount)}")
            time.sleep(100.0)
            continue

        result = judgment(0)
        if result == "wait":
            okflag = 0
            print("等待 不用處理")
        elif result == "next":
            okflag = 0
            print("下一筆")
            swipe_start = '500 1300'
            swipe_end = '500 100'
            swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
            time.sleep(6.0)
            if (resolution_height > 2000):
                jump = 200 + BaseJump
            else:
                jump = 150 + BaseJump
            Shopeecount = Shopeecount + 1
            ErrorCount = 0
        elif result == "ok":
            if okflag == 1 :
                 # 關閉 Shopee
                device.shell(f"am force-stop {package_name}")
                print("Shopee 已停止")
                time.sleep(4.0)
                # 啟動 Shopee
                start_command = f"am start -n {package_name}/{activity_name}"
                output = device.shell(start_command)
                print(f"Shopee 已啟動，輸出：\n{output}")
                time.sleep(6.0)
        
                tap(device, str((resolution_width / 2) + 50) + " " + str((resolution_height) - 150))
                #tap(device, "545 2180 ")
                time.sleep(4.0)
                okflag = 0
                continue
            Shopeecount = 0
            if (resolution_height > 2000):
                jump = 200 + BaseJump
            else:
                jump = 150 + BaseJump
            ErrorCount = 0
            turn_on_screen()
            okflag = 1
            continue
    
        print("重複")
    
        last_date = datetime.date.today()
    except Exception as ex:
        print(f"有重大錯誤{ex.args[0]}")
   