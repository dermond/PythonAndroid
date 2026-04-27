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
import uiautomator2 as u2
import traceback

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

# Shopee 的包名與主 Activity
package_name = "com.shopee.tw"
activity_name = "com.shopee.app.ui.home.HomeActivity_"

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

   #  subprocess.run([
   #      "adb", "-s", device_id, 
   #      "shell", "wm", "size", f"{resolution_width}x{resolution_height}"
   #  ])
   #  time.sleep(1)
   #  subprocess.run(["adb", "-s", device_id, "shell", "wm", "size", "reset"])

   #  subprocess.run(["adb", "-s", device_id, "shell", "wm", "size", "reset"], check=False)

   #  subprocess.run(["adb", "-s", device_id, "shell", "wm", "density", "reset"], check=False)

   #  subprocess.run(["adb", "-s", device_id, "shell", "wm", "overscan", "reset"], check=False)

   # # 1. 重置螢幕尺寸與密度 (這兩項在 Android 11+ 依然有效)
   #  subprocess.run(["adb", "-s", device_id, "shell", "wm", "size", "reset"], check=False)
   #  subprocess.run(["adb", "-s", device_id, "shell", "wm", "density", "reset"], check=False)

   #  # 2. 清除沉浸模式 (Immersive Mode) 設定
   #  subprocess.run(["adb", "-s", device_id, "shell", "settings", "put", "global", "policy_control", "null"], check=False)
   #  subprocess.run(["adb", "-s", device_id, "shell", "settings", "delete", "global", "policy_control"], check=False)

   #  # 3. 重置導航模式 (針對 Android 11+ 的核心重置)
   #  # 這裡我們先嘗試「啟用」三鍵導航模式 (最傳統的導航列)
   #  print("正在恢復三鍵導航模式...")
   #  subprocess.run(["adb", "-s", device_id, "shell", "cmd", "overlay", "enable", "com.android.internal.systemui.navbar.threebutton"], check=False)
    
   #  # 如果你想重置回手勢導航，可以改用下面這行：
   #  # subprocess.run(["adb", "-s", device_id, "shell", "cmd", "overlay", "enable", "com.android.internal.systemui.navbar.gestural"], check=False)

   #  time.sleep(1)

   #  subprocess.run(["adb","-s",device_id,"shell","settings","put","secure","navigation_mode","0"])
   #  subprocess.run(["adb","-s",device_id,"shell","pkill","com.android.systemui"])
   #  time.sleep(1)

   #  # 4. 強制重啟 SystemUI 讓設定生效
   #  print("重啟 SystemUI...")
   #  subprocess.run(["adb", "-s", device_id, "shell", "pkill", "com.android.systemui"], check=False)

   #  print("重置完成！")
   #  time.sleep(2)
    
    


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
         # 取得 resource-id（避免報錯）
        resource_id = ""
        if hasattr(item, "attrib"):
            resource_id = item.attrib.get("resource-id", "")
        elif hasattr(item, "info"):
            resource_id = item.info.get("resourceName", "")

        # 👉 排除系統時間
        if resource_id == "com.android.systemui:id/clock":
            continue
        
        text = item.text
        
        # 避免 None
        if not text:
            continue
        
        text = text.strip()

        # 浮點數 0 ~ 5
        if float_value is None and re.fullmatch(r'0*(?:[0-4](?:\.\d+)?|5(?:\.0*)?)', text):
            float_value = float(text)

        # 時間格式 mm:ss 或 hh:mm
        elif time_value is None and re.fullmatch(r'\d{1,2}:\d{2}', text):
            time_value = text

        # 找齊就直接跳出（加速）
        if float_value is not None and time_value is not None:
            return True, float_value, time_value

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

def count_text_elements(device_id, text_to_find, retries=3, delay=1):
    """
    計算畫面上符合指定文字的元素數量
    
    :param device_id: 裝置ID
    :param text_to_find: 要查找的文字
    :param retries: 找不到時重試次數
    :param delay: 每次重試間隔秒數
    :return: 數量 (int)
    """
    d = u2.connect(device_id)
    
    try:
        for attempt in range(1, retries + 1):
            elements = d.xpath(f'//*[@text="{text_to_find}"]').all()
            count = len(elements)

            if count > 0:
                return count
            else:
                if attempt < retries:
                    print(f"文字 '{text_to_find}' 未找到，等待 {delay} 秒後重試 ({attempt}/{retries})...")
                    time.sleep(delay)
                else:
                    print(f"文字 '{text_to_find}' 未找到，已達最大重試次數 ({retries})")
                    return 0

    except Exception as ex:
        return 0

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
    try:
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
    except Exception as ex:
        return None
    return None

 
def click_shopee_activity_by_coord(d, target_x=540, target_y=1800):
    """
    In cases where 'bounds' is not allowed, we use coordinate-based 
    interaction combined with a check for a 'clickable' container 
    at the relevant depth.
    """
    print(f"Targeting interaction point: ({target_x}, {target_y})")
    
    # 1. Look for the interactive container by ClassName and Clickable status
    # In Shopee Video, these layers are usually 'android.view.View' 
    # and are marked as clickable even if they have no text.
    layers = d(className="android.view.View", clickable=True)
    
    found_target = False
    
    for layer in layers:
        # Since we can't check 'bounds' directly in the selector, 
        # we pull the info to see if our target point (1800) falls inside.
        info = layer.info
        top = info['range']['top'] if 'range' in info else info['visibleBounds']['top']
        bottom = info['range']['bottom'] if 'range' in info else info['visibleBounds']['bottom']
        
        # Check if our 1800 Y-coordinate is within this layer's vertical span
        if top <= target_y <= bottom:
            print(f"Found active layer: {info.get('resourceName', 'Unknown Resource')}")
            found_target = True
            break
            
    if found_target:
        print(f"Executing click at ({target_x}, {target_y})")
        d.click(target_x, target_y)
        return True
    else:
        # Fallback: Forced click if the hierarchy is too complex to parse
        print("Layer not confirmed, attempting blind click at target coordinates.")
        d.click(target_x, target_y)
        return True

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
   
def Key_Return():
    try:
        subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "4"], check=True)
  
        print("Key_Return")
    except Exception as e:
        print(f"Key_Return 錯誤")

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

def find_imageview_by_bounds(d, target_bounds, width_tolerance=10, height_tolerance=10):
    """
    在 uiautomator2 裡找出 className = android.widget.ImageView 且 bounds 接近 target 的元素
    
    參數:
        d: uiautomator2 device 連線物件
        target_bounds: [left, top, right, bottom]
        width_tolerance: 寬度容差
        height_tolerance: 高度容差
    
    回傳:
        最接近的元素 UiObject 或 None
    """
    target_class = "android.widget.ImageView"

    def parse_bounds(b):
        # 將 bounds 字串轉成 [x1, y1, x2, y2]
        b = b.replace('[','').replace(']',' ').split()
        x1, y1 = map(int, b[0].split(','))
        x2, y2 = map(int, b[1].split(','))
        return [x1, y1, x2, y2]

    target_width = target_bounds[2] - target_bounds[0]
    target_height = target_bounds[3] - target_bounds[1]

    candidates = []

    for el in d.xpath(f'//*[@package="com.shopee.tw"]').all():
        b_str = el.attrib.get("bounds")
        if not b_str:
            continue
        b = parse_bounds(b_str)
        width = b[2] - b[0]
        height = b[3] - b[1]

        # 比對寬高
        if abs(width - target_width) <= width_tolerance and abs(height - target_height) <= height_tolerance:
            # 計算與 target 差距（越小越好）
            diff = abs(b[0]-target_bounds[0]) + abs(b[1]-target_bounds[1]) \
                   + abs(b[2]-target_bounds[2]) + abs(b[3]-target_bounds[3])
            candidates.append((diff, el))

    if not candidates:
        return None

    # 選擇最接近的元素
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def All_Close():
    global d
    if d(resourceId="com.shopee.tw.dfpluginshopee7:id/ic_close").exists:
        #print("發現蝦皮關閉按鈕，正在點擊...")
        d(resourceId="com.shopee.tw.dfpluginshopee7:id/ic_close").click()
    if d(resourceId="com.shopee.tw.dfpluginshopee7:id/img_close").exists:
        #print("發現蝦皮關閉按鈕，正在點擊...")
        d(resourceId="com.shopee.tw.dfpluginshopee7:id/img_close").click()
    if d(resourceId="com.shopee.tw.dfpluginshopee7:id/fl_content").exists:
        print("fl_content")
        Key_Return()
        

    target_bounds = [493, 1743, 587, 1837]
    el = find_imageview_by_bounds(d, target_bounds, width_tolerance=0, height_tolerance=0)
    if el:
        print("找到元素:", el.attrib)
        # 點擊
        el.click()
    else:
        print("找不到符合條件的元素")
              
if __name__ == '__main__':
  
  goflag = 0
  deviceid = ""
  #deviceid = "R58N10RXWVF"
  #deviceid = "46081JEKB10015"
  #deviceid = "de824891"
  #deviceid = "FA75V1802306"
  
  if len(sys.argv) > 1:
        print("你輸入的參數如下：")
        for i, arg in enumerate(sys.argv[1:], start=1):
            print(f"參數 {i}：{arg}")
        deviceid = str(sys.argv[1])
  else:
    print("沒有輸入任何參數")
  
 
  device, client = connect(deviceid)
  adb_init(deviceid)
  device_id = device.serial

  ReLoadShopee()
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
    
  Step = 0

  LimitTotalCount = SettingReader.getSetting("base",deviceid + "LimitTotalCount")
  if LimitTotalCount == '':
      LimitTotalCount = 80
      SettingReader.setSetting("base",deviceid + "LimitTotalCount", LimitTotalCount )

  TotalCount = SettingReader.getSetting("base",deviceid + "TotalCount")
  if TotalCount == '':
      TotalCount = 0
      SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
  TotalCount = int(TotalCount)

 
  print("正在獲取螢幕物件配置...")
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


          
          start_time = datetime.time(1, 00)   
          end_time   = datetime.time(1, 10)  
          # ✅ 只有在 08:00~11:00 之間
          if start_time <= now <= end_time:
          #進行
            Step = 0
           
          print(f"TotalCount：\n{str(TotalCount)}")
          if int(TotalCount) > int(LimitTotalCount):
            print(f"TotalCount 大於"+str(LimitTotalCount)+f"次：\n{str(TotalCount)}")
            
            continue

          # 連接手機 (如果只有一台手機，通常不用填 serial
          print("---Start---------...")
          #time.sleep(1.0)
          allspace = True
          d = u2.connect(device_id)
          #time.sleep(1.0)
          cancelflag = False
          
          #Step == 0 點選直播短影音
          #Step == 1 短影音
          #Step == 20 直播
          #Step == 10 下一場次
          #Step == 30 領取
          
          if i % 100 == 0 and i != 0:
            print(f"現在跑到第 {i} 次，做一次處理")
            if Step == 30:
               ReLoadShopee()
               Step = 20
            else:
               ReLoadShopee()
               Step = 0
          # 獲取當前頁面所有元素
          # 使用 xpath 抓取所有節點
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
                print("-" * 30)

                if text == "直播短影音" and Step == 0:
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    Step = 1
                    break

                if text == "參加":
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    break
                if text == "打開簽到":
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    break

                if text == "關注":
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    break
                if text == "立即簽到":
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    break
                if text == "簽到獲得獎勵":
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    ReLoadShopee()
                    break
                if text.find("完成簽到，即可獲得") > -1:
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    ReLoadShopee()

                    break
                if text == "下一場次" and Step == 10:
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    
                    break
                if text == "簽到":
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    # 觸發系統「返回鍵」
                    d.press("back")
                    time.sleep(2.0)
                    break
                if text == "領取" and Step != 30:
                    click_bounds(d, bounds)
                    allspace =False
                    time.sleep(2.0)
                    # 觸發系統「返回鍵」
                    d.press("back")
                    time.sleep(2.0)
                    el = d.xpath('//*[@text="短影音"]').get()
                    bounds = el.attrib.get('bounds')

                    click_bounds(d, bounds)

                    
                    break
                if text == "領取" and Step == 30:
                    nums = re.findall(r'\d+', bounds)
                    if len(nums) == 4:
                        left, top, right, bottom = map(int, nums)
                        # 計算中心點
                        center_x = (left + right) // 2
                        center_y = (top + bottom) // 2

                    option_position = str(center_x) + ' ' + str(center_y - 50)    # 選擇的選項的位置
                    
                    d = u2.connect(device_id)
                    screen_width = d.info.get('displayWidth') 
        
                    # 2. 動態計算右側 1/3 的門檻
                    right_threshold = (screen_width / 3) * 2

                    # 3. 判斷中心點是否大於門檻
                    if center_x >= right_threshold:
                        tap(device, option_position) 
                        time.sleep(2.0)

                        print(f"螢幕寬度: {screen_width}, 門檻: {right_threshold}")
                        print(f"符合條件：按鈕在右側 (x={center_x})")
            
                        option_position = str(center_x) + ' ' + str(center_y - 50)
                        tap(device, option_position) 
                        time.sleep(2.0)
            
                        # 後續邏輯保持不變
                        for el in d.xpath('//*').all():
                            text_val = el.text
                            if text_val:
                                print(f"內容: {text_val} | 位置: {el.attrib.get('bounds')}")
            
                        All_Close()
                        TotalCount = int(TotalCount) + 1
                        SettingReader.setSetting("base", deviceid + "TotalCount", str(TotalCount))
                    else:
                        print(f"跳過：按鈕 x={center_x} 不在右側區域 (門檻 {right_threshold})")

                   
                    #SettingReader.setSetting("base",deviceid + "TotalCount", str(TotalCount) )
                
                if text == "觀看"and Step != 10: 
               
                    allspace =False
                    # 觸發系統「返回鍵」
                    Key_Return()
                    time.sleep(2.0)
                    
                    break
                if text == "觀看" and Step == 10:
               
                    allspace =False
                    # 觸發系統「返回鍵」
                    Key_Return()
                    time.sleep(2.0)
                    
                    el = d.xpath('//*[@text="短影音"]').get()
                    bounds = el.attrib.get('bounds')
                    click_bounds(d, bounds)
                    Step = 51
                    break
                #if text == "推薦":
                   #click_bounds(d, bounds)
                   #time.sleep(2.0)
                   #frame1flag = 1
                   
                if text == "直播" and Step == 20:
                   allspace =False
                   click_bounds(d, bounds)
                   time.sleep(2.0)
                   Step = 30
                   tap(device, str((resolution_width / 2)) + " " + str((resolution_height / 2) -200 ))
                   break
                   #Key_Return()
                if text == "短影音" and (Step == 1 or Step == 51):
                   allspace =False
                   click_bounds(d, bounds)
                   time.sleep(2.0)
                   if (Step == 1):
                       Step = 10
                       
                   if (Step == 51):
                       Step = 52
                   tap(device, str((resolution_width / 2)) + " " + str((resolution_height / 2) -200 ))
                   break
                if text == "我的" and Step == 52:
                   allspace =False
                   click_bounds(d, bounds)
                   time.sleep(2.0)
                   Step = 53
                   allspace =False
                   #tap(device, str((resolution_width / 2)) + " " + str((resolution_height / 2) -200 ))
                   break
                if text == "我的蝦幣" and Step == 53:
                   click_bounds(d, bounds)
                   time.sleep(2.0)
                   Step = 54
                   allspace =False
                   #tap(device, str((resolution_width / 2)) + " " + str((resolution_height / 2) -200 ))
                   break
            
                if text == "簽到並開啟寶箱" and Step == 54:
                   click_bounds(d, bounds)
                   time.sleep(2.0)
                   
                   allspace =False
                   d.press("back")
                   time.sleep(2.0)
                   Step = 55
                   #tap(device, str((resolution_width / 2)) + " " + str((resolution_height / 2) -200 ))
                   break
                if text == "剩餘機會 : " and (Step == 54 or Step == 55):
                   nums = re.findall(r'\d+', bounds)
                   if len(nums) == 4:
                       left, top, right, bottom = map(int, nums)
                       # 計算中心點
                       center_x = (left + right) // 2
                       center_y = (top + bottom) // 2

                   option_position = str(center_x) + ' ' + str(center_y - 100)    # 選擇的選項的位置
                   tap(device, option_position) 
                   time.sleep(2.0)
                   Step = 56
                   allspace =False
                   #tap(device, str((resolution_width / 2)) + " " + str((resolution_height / 2) -200 ))
                   break
                if text == "幸運轉盤":
                    # 截圖並裁剪
                    start_point = ((resolution_width / 2 ) - 150, (resolution_height / 2 ) - 250)  # 起始坐標 (x, y)
                    end_point = ((resolution_width / 2 ) + 150, (resolution_height / 2 ) + 50)    # 結束坐標 (x, y)

                    img = capture_screenshot(device)
                    cropped_img = crop_image(img, start_point, end_point)
                    resulttext = paddleocr_image(cropped_img)  

                    actionx = (resolution_width / 2 )
                    actiony = (resolution_height / 2 ) -100
                    click_action(d, actionx , actiony)
                    allspace =False
                    time.sleep(2.0)
                    d.press("back")
                    break
                if text == "正在計算中...":
                    Key_Return()
                    Step = 10
                    break
                #if d(resourceId="com.shopee.tw.dfpluginshopee7:id/main_play_layout").exists:
                #    #print("發現蝦皮關閉按鈕，正在點擊...")
                #    d(resourceId="com.shopee.tw.dfpluginshopee7:id/main_play_layout").click()
                #    #allspace =False
                #    time.sleep(2.0)

                #else:
                #    print("未發現關閉按鈕")

       

                if text == "瀏覽獲獎結果":

                    index = (resolution_height / 2 ) + 282
                    tap(device, str(resolution_width / 2) + " " + str(index))
                    time.sleep(2.0)

                    #滑動
                    swipe_start = '500 1300'
                    swipe_end = '500 500'
                    swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
                    time.sleep(2.0)
                    allspace =False
                    break
               
                if text.find("前往驗證") > -1 :
                    cancelflag = True
                    #break
                if text.find("成功獲得") > -1 or text.find("下單 +1") > -1 or text.find("免費機會") > -1:
                    Key_Return()
                    time.sleep(2.0)
                    Step = 20
                    cancelflag = True
                                       
                    el = d.xpath('//*[@text="直播短影音"]').get()
                    bounds = el.attrib.get('bounds')
                    click_bounds(d, bounds)
                    time.sleep(2.0)
                    break
                
                if text == "取消":
                    if cancelflag :
                        click_bounds(d, bounds)
                        allspace =True
                    break
            else:
                # 獲取座標 (attrib 裡面的 bounds)
                 bounds = el.attrib.get('bounds')
                # # 獲取類別
                 classname = el.attrib.get('class')

                 print(f"內容: {text}")
                 print(f"位置: {bounds}")
                 print(f"類型: {classname}")

                 # 嘗試列印出所有屬性看看
                 print(el.attrib)
                 # 在您的程式碼中加入這一行
                 description = el.attrib.get('content-description') or el.attrib.get('content-desc')
                 print(f"說明標籤: {description}")

          if allspace :
           # click_shopee_activity_by_coord(d)
            All_Close()

            if Step == 30:
              valid, value, time2 = validate_block(d.xpath('//*').all())
              if valid:
                print("找到數值或是時間")
                continue  
              else:
                print("沒有找到數值或是時間")
            ## 判斷說明標籤為 "close product panel" 的元素是否存在
            #if d(description="close product panel").exists:
            #    print("發現商品面板關閉按鈕，執行點擊...")
            #    d(description="close product panel").click()
            #else:
            #    print("未發現按鈕，跳過。")

            swipe_start = '500 1300'
            swipe_end = '500 500'
            swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
            time.sleep(2.0)
      except Exception as ex:
        # 正確寫法 1：直接印出完整錯誤（最常用）
        traceback.print_exc()
    
        # 正確寫法 2：將錯誤轉成字串（存入變數，方便寫入 Log）
        full_error = traceback.format_exc()
        print(f"完整錯誤資訊：\n{full_error}")





  #if (resolution_width == 1440):
  #    Leftspace = 340
  #if (density >= 640):
  #    dpi = 20

  #if (resolution_height > 2000 and density == 640):
  #     jump = 300

  #if (resolution_height > 2000 and density == 480):
  #     jump = 200
  ## #錯誤視窗判斷
  ## Shopee 的包名與主 Activity
  #package_name = "com.shopee.tw"
  #activity_name = "com.shopee.app.ui.home.HomeActivity_"
  
  #Shopeecount = 0
  #ErrorCount = 0
  
  #LimitTotalCount = SettingReader.getSetting("base",deviceid + "LimitTotalCount")
  #if LimitTotalCount == '':
  #    LimitTotalCount = 80
  #    SettingReader.setSetting("base",deviceid + "LimitTotalCount", LimitTotalCount )

  #TotalCount = SettingReader.getSetting("base",deviceid + "TotalCount")
  #if TotalCount == '':
  #    TotalCount = 0
  #    SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
  #TotalCount = int(TotalCount)
  

  #today = datetime.date.today()
  #yesterday = today - datetime.timedelta(days=1)
  
  #(xpoint,ypoint) =convert_xy_with_dpi(130,430);
  #for i in range(99999999):
  #  try:

  
  #      current_date = str(datetime.date.today())
  #      getdate = SettingReader.getSetting("base",deviceid + "date")
    
  #      TotalCount = SettingReader.getSetting("base",deviceid + "TotalCount")
    
  #      # 如果是空字串，給預設值 0
  #      if TotalCount == "" or TotalCount is None:
  #          TotalCount = 0
  #          SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
    
  #      if getdate != current_date:
  #          TotalCount = 0
  #          SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
  #          SettingReader.setSetting("base",deviceid + "date", current_date )
  #          adb_init(deviceid)
        
  #      now = datetime.datetime.now().time()

  #      start_time = datetime.time(5, 0)    # 05:00
  #      end_time   = datetime.time(5, 30)   # 05:30

  #      # ✅ 只有在 05:00~05:30 之間
  #      if start_time <= now <= end_time:
  #          TotalCount = 0
  #          SettingReader.setSetting("base",deviceid + "TotalCount", TotalCount )
  #          SettingReader.setSetting("base",deviceid + "date", current_date )
  #          adb_init(deviceid)

  #      check_garbage_objects()
  #      print_memory_usage()
  #      turn_off_screen()
  #      if Shopeecount > 10:  # 如果 i 是 10 的倍數
  #          print(f"第 {i} 次操作：重啟 Shopee App")
        
           
  #          ReLoadShopee()
  #          # tap(device, "740 190 ")
  #          # time.sleep(3.0)
        
  #          # tap(device, "322 1263 ")
  #          # time.sleep(1.0)
  #          Shopeecount = 0
        
  #      start_time = datetime.time(8, 0)    # 08:00
  #      end_time   = datetime.time(11, 00)   # 11:00
  #      # ✅ 只有在 08:00~11:00 之間
  #      if start_time <= now <= end_time:
  #          #進行
  #          Nextshow(0)


  #      now = datetime.datetime.now()
  #      now_time = now.time()
  #      weekday = now.weekday()  # 0 = 星期一, 6 = 星期日

  #      # 定義每天的禁止執行時間區段（start_time, end_time）
  #      restricted_times = {
  #          0: (datetime.time(3, 0), datetime.time(13, 0)),   # 星期一
  #          1: (datetime.time(3, 0), datetime.time(13, 0)),   # 星期二
  #          2: (datetime.time(3, 0), datetime.time(13, 0)),   # 星期三
  #          3: (datetime.time(3, 0), datetime.time(13, 0)),   # 星期四
  #          4: (datetime.time(3, 0), datetime.time(13, 0)),   # 星期五
  #          5: (datetime.time(3, 0), datetime.time(13, 0)),   # 星期六
  #          6: (datetime.time(3, 0), datetime.time(13, 0)),   # 星期日
  #      }

  #      start, end = restricted_times[weekday]

  #      # 判斷是否在禁止區段內（處理跨午夜的情況）
  #      in_restricted = False
  #      if start < end:
  #          # 時間區段沒有跨午夜
  #          in_restricted = start <= now_time < end
  #      else:
  #          # 時間區段跨午夜，例如 23:00 ~ 10:00
  #          in_restricted = now_time >= start or now_time < end

  #      if in_restricted:
  #          print(f"現在時間 {now_time} 在禁止區段 ({start}~{end})，跳過執行，時間：{now}")
  #          time.sleep(10.0)
        
  #          #滑動
  #          swipe_start = '500 1300'
  #          swipe_end = '500 500'
  #          swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
  #          time.sleep(2.0)

  #          if goflag == 0 :
  #              device.shell(f"am force-stop {package_name}")
  #              print("Shopee 已停止")
  #              time.sleep(2.0)
            
  #          goflag = 1
  #          nextsession = 0
  #          continue

  #      if goflag == 1 :
  #          # 啟動 Shopee
  #          start_command = f"am start -n {package_name}/{activity_name}"
  #          output = device.shell(start_command)
  #          print(f"Shopee 已啟動，輸出：\n{output}")
  #          time.sleep(4.0)
        
  #          tap(device, str((resolution_width / 2) + 50) + " " + str((resolution_height) - 200))
  #          #tap(device, "545 2180 ")
  #          time.sleep(2.0)
  #      goflag = 0

  #      # 如果不在禁止區段，就執行你的主程式
  #      print(f"現在時間 {now_time} 可以執行，時間：{now}")
    
  #      print(f"TotalCount：\n{str(TotalCount)}")
  #      if int(TotalCount) > int(LimitTotalCount):
  #          print(f"TotalCount 大於"+str(LimitTotalCount)+f"次：\n{str(TotalCount)}")
  #          time.sleep(100.0)
  #          continue

  #      result = judgment(0)
  #      if result == "wait":
  #          okflag = 0
  #          print("等待 不用處理")
  #      elif result == "next":
  #          okflag = 0
  #          print("下一筆")
  #          swipe_start = '500 1300'
  #          swipe_end = '500 100'
  #          swipe_to_position(device, swipe_start, swipe_end)  # 确保屏幕滚动到固定位置
  #          time.sleep(6.0)
  #          if (resolution_height > 2000):
  #              jump = 200 + BaseJump
  #          else:
  #              jump = 150 + BaseJump
  #          Shopeecount = Shopeecount + 1
  #          ErrorCount = 0
  #      elif result == "ok":
  #          if okflag == 1 :
  #               # 關閉 Shopee
  #              device.shell(f"am force-stop {package_name}")
  #              print("Shopee 已停止")
  #              time.sleep(4.0)
  #              # 啟動 Shopee
  #              start_command = f"am start -n {package_name}/{activity_name}"
  #              output = device.shell(start_command)
  #              print(f"Shopee 已啟動，輸出：\n{output}")
  #              time.sleep(6.0)
        
  #              tap(device, str((resolution_width / 2) + 50) + " " + str((resolution_height) - 150))
  #              #tap(device, "545 2180 ")
  #              time.sleep(4.0)
  #              okflag = 0
  #              continue
  #          Shopeecount = 0
  #          if (resolution_height > 2000):
  #              jump = 200 + BaseJump
  #          else:
  #              jump = 150 + BaseJump
  #          ErrorCount = 0
  #          turn_on_screen()
  #          okflag = 1
  #          continue
    
  #      print("重複")
    
  #      last_date = datetime.date.today()
  #  except Exception as ex:
  #      print(f"有重大錯誤{ex.args[0]}")
   