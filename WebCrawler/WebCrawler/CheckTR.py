# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 12:23:27 2021

@author: dermo
"""
import psutil
from pickle import FALSE, TRUE
import shlex
import shutil
import os
import sys
import traceback
import time
import datetime
import uuid
import math
import json
import re
import requests
from io import StringIO
import pandas as pd
import numpy as np
import pyodbc
from selenium import webdriver
import Service.PublicFun as PublicFun
import Service.SettingReader as SettingReader
import Service.SpiderHandler as SpiderHandler
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import Service.SQLConnect as SQLConnect
#from shapely.geometry import Polygon, Point
import threading
import logging
from logging.handlers import TimedRotatingFileHandler
from selenium.common.exceptions import TimeoutException
import subprocess
import chardet
import psutil
import urllib3

urllib3.disable_warnings()

temp_Path= r"C:\Users\dermo\Downloads"
featuresIndex = 0

# 設置日誌級別
logging.basicConfig(level=logging.INFO)

urllib3.disable_warnings()

# 設置日誌文件名和輪替方式
handler = TimedRotatingFileHandler(filename='example.log', when='midnight', backupCount=7)

# 設置日誌格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 添加處理程序到 logger 對象
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# 檔案列表和相關程序的對應關係
files_to_monitor = {
    
}
def kill_process_by_path(target_path):
    """ 根據可執行文件路徑終止進程 """
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['exe'] == target_path:
                proc.kill()  # 終止進程
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # 忽略無法訪問或已經不存在的進程
def start_process(path):
    """ 啟動一個新進程 """

    working_directory = os.path.dirname(path)
            
    subprocess.Popen(path, cwd=working_directory)

    

def get_file_modification_time(file_path):
    """ 獲取檔案的最後修改時間 """
    mod_time = os.path.getmtime(file_path)
    return datetime.datetime.fromtimestamp(mod_time)

def first_programs():
    for file_path, program in files_to_monitor.items():
        working_directory = os.path.dirname(program)

        start_process(program)
       
        #subprocess.Popen(program, cwd=working_directory)
def kill_all_chrome_processes():
    """終止所有 Chrome 進程"""
    for proc in psutil.process_iter(['name']):
        try:
            # 檢查進程名是否為 Chrome 的可執行文件
            if 'chrome' in proc.name().lower():
                proc.terminate()  # 嘗試優雅終止進程
                try:
                    proc.wait(timeout=3)  # 等待最多3秒
                except psutil.TimeoutExpired:
                    proc.kill()  # 如果進程在給定時間內未終止，則強制終止
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # 忽略無法訪問或已經不存在的進程


def check_files_and_restart_programs():
    """ 檢查檔案並在需要時重啟程序 """
    allkill = TRUE
    for file_path, program in files_to_monitor.items():
        last_mod_time = get_file_modification_time(file_path)
        if datetime.datetime.now() - last_mod_time > datetime.timedelta(minutes=30):
            print(f"檔案 {file_path} 最後修改時間超過30分鐘，將重新啟動 {program}")
            # 關閉程序
            try:
                if allkill:
                    #kill_all_chrome_processes()
                    allkill = FALSE

                kill_process_by_path(program)
                #exit_code = os.system(f"taskkill /F /IM \"{program}\"")
                #result = subprocess.run(["taskkill", "/F", "/IM", program], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='cp437')
            except subprocess.CalledProcessError as e:
                print("命令執行失敗，返回碼:", e.returncode)
                print("錯誤輸出:", e.stderr)
            except Exception as e2:
                print("捕獲到未預期的異常:", str(e2))
            # 確認程序已關閉
            time.sleep(5)
            # 重新啟動程序
            working_directory = os.path.dirname(program)
            start_process(program)
            #subprocess.Popen(program, cwd=working_directory)
        else:
            print(f"檔案 {file_path} 狀態正常")

def ini_to_dict(section):
    """將 INI 文件指定 section 轉換為 JSON"""
    from configparser import RawConfigParser

    filepath=os.getcwd()
    settingfilePath=os.path.join(filepath,"setting.ini")

    with open(settingfilePath, 'rb') as f:
        result = chardet.detect(f.read())
        file_encoding = result['encoding']

    parser = RawConfigParser()
    parser.read(settingfilePath, encoding=file_encoding)
    
    data = {}
    if parser.has_section(section):
        items = parser.items(section)
        settings = {k: v for k, v in items if k.startswith('setting')}
        programs = {k: v for k, v in items if k.startswith('program')}

        for k, v in settings.items():
            # 假設 setting 和 program 的編號是匹配的
            program_key = 'program' + k[len('setting'):]
            data[v] = programs.get(program_key, '')  # 使用 setting 的值作為 key，對應的 program 作為 value

    return data
# 指定您的 INI 文件路徑

if __name__ == '__main__':    
    
   
    files_to_monitor = ini_to_dict('Exec')

    try:
        first_programs()
        time.sleep(1000)
        while True:
            check_files_and_restart_programs()
            # 每隔一段時間檢查一次，例如每30分鐘
            time.sleep(1000)
       
    except Exception as e:
        print("程式內出現無法預測的錯誤:")

    