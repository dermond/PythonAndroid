# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 12:23:27 2021

@author: dermo
"""
import psutil
from pickle import TRUE
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

temp_Path= r"C:\Users\dermo\Downloads"
featuresIndex = 0

# 設置日誌級別
logging.basicConfig(level=logging.INFO)


# 設置日誌文件名和輪替方式
handler = TimedRotatingFileHandler(filename='example.log', when='midnight', backupCount=7)

# 設置日誌格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 添加處理程序到 logger 對象
logger = logging.getLogger(__name__)
logger.addHandler(handler)



def square_point(lat, lng, distance = 1.0):
    EARTH_RADIUS = 6371.0
    dlng = 2 * math.asin(math.sin(distance / (2 * EARTH_RADIUS) / math.cos(math.radians(lat))))
    dlng = math.degrees(dlng)
    dlat = distance / EARTH_RADIUS
    dlat = math.degrees(dlat)
    return dlat, dlng

def deg2rad(deg):
    return deg * (math.pi / 180)

def rad2deg(rad):
    return rad * (180 / math.pi)  

def is_point_inside_polygon(x, y, poly):
    """
    判断点 (x,y) 是否在多边形 poly 内部
    poly 是一个由多个点坐标组成的列表
    """
    # 射线起点
    start = (x, y)
    # 射线终点（取多边形顶点的横坐标最大值加 1 作为终点）
    end = (max(poly, key=lambda p: p[0])[0] + 1, y)
    # 统计交点个数
    count = 0
    for i in range(len(poly)):
        p1 = poly[i]
        p2 = poly[(i + 1) % len(poly)]
        # 判断射线与边是否相交
        if ((p1[1] > y) != (p2[1] > y)) and (x < (p2[0] - p1[0]) * (y - p1[1]) / (p2[1] - p1[1]) + p1[0]):
            count += 1
    # 判断交点个数的奇偶性
    return count % 2 == 1

# 創建一個空的快取字典
name_cache = {}

def execute_name(name):
   if name in name_cache:  # 檢查名稱是否存在於快取中
        return True
   else:
        name_cache[name] = True  # 寫入名稱到快取中
        return False

def get_memory_usage_percentage():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_usage = memory_info.rss  # in bytes
    total_memory = psutil.virtual_memory().total
    memory_usage_percent = (memory_usage / total_memory) * 100
    return memory_usage_percent

def extract_lat_lng_from_google_maps_url(url):
    # 正則表達式匹配緯度和經度
    pattern = r'/@([-\d.]+),([-\d.]+)'
    match = re.search(pattern, url)

    if match:
        lat, lng = match.groups()
        return float(lat), float(lng)
    else:
        return None, None

def scanPoints(driver,lat,lon,TargetName,TargetUrl,TargetGUID):
       
    DBConnect = SQLConnect.DBConnect()
    try:
  
        driver.get(TargetUrl)  # 輸入範例網址，交給瀏覽器
        
       
        print("單筆資料")
        QyI6Nb = ui.WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME , "QyI6Nb")))  
        #QyI6Nb =  driver.find_element(By.CLASS_NAME,".QyI6Nb")
        QyI6Nb.click()
        time.sleep(2)
        try:
           

            isCloseing = False
            name = driver.find_element(By.CSS_SELECTOR,".DUwDvf").text

            if name == '':
                return

            if TargetName != name:
                logger.error("地點名稱不一致" +str(TargetName)+"&"+str(TargetGUID) + ":" +str(TargetUrl))

                 #名稱有問題
                sql_cmd = "UPDATE Nearbysearch set "
                sql_cmd += "Status = N'-1' "
   
                sql_cmd += " WHERE GUID = '"+ TargetGUID +"'" 
            
                DBConnect.ConnectDB()
                DBConnect.Execute(sql_cmd);
                DBConnect.close()
                print(TargetName + "    " + TargetUrl)
                return

            W4Efsds = driver.find_elements(By.CSS_SELECTOR,".F7nice")
            ratings = W4Efsds[0].text.split("(")[0].strip()
            result = re.findall(pattern, ratings)
                     
            if result:
                ratings = str(float(result[0]))
                #print(number)
            else:
                ratings = str(0)

                          
            if ( len(W4Efsds[0].text.split("(")) >= 2 ):
                if ( W4Efsds[0].text.split("(")[1].split(")")[0].find("\x00") > -1 ):
                    print("sergerg")
                user_total_ratings = W4Efsds[0].text.split("(")[1].split(")")[0].split("\x00")[0].replace(",","").strip()
            else:
                return

            for W4Efsd in W4Efsds:
                if (W4Efsd.text.find("永久停業") > -1):
                    isCloseing = True
            types =driver.find_element(By.CSS_SELECTOR,".DkEaL").text.split("·")[0].split("\n")[0].strip()
                             
            if (types.find("營業時間") > -1):
                types=''
                           


            href = driver.current_url

            newlat, newlng = extract_lat_lng_from_google_maps_url(href)

            if execute_name(str(name) + str(newlat) + str(newlng)):
                              
                return


           

            sql_cmd = "select * from Nearbysearch where GUID ='"+TargetGUID+"'"
            DBConnect.ConnectDB()
            Nearbysearchdt = DBConnect.GetDataTable(sql_cmd)
            DBConnect.close()

            dttypes = Nearbysearchdt[0].types.split("@@")
            # 將列表轉換成集合以去除重複元素
            types_set = set(dttypes)
            # 檢查新類型是否已在集合中
    
            if types not in types_set:
                # 如果不在集合中，則添加它
                types_set.add(types)
            # 將更新後的集合轉換回列表
            dttypes = list(types_set)
            # 如果需要，將更新後的類型列表轉換回字符串
            new_types_str = "@@".join(dttypes)



            #確定下載了 才會記錄
            sql_cmd = "UPDATE Nearbysearch set "
            sql_cmd += "Status = N'0',"
            if (isCloseing):
                sql_cmd += "IsClose ='1'"
            else:
                sql_cmd += "IsClose ='0'"

            sql_cmd += " WHERE GUID = '"+ TargetGUID +"'" 
            
            DBConnect.ConnectDB()
            DBConnect.Execute(sql_cmd);
            DBConnect.close()
 
                               

        except Exception as e:
                           
            logger.error("featuresIndex1:" +str(featuresIndex) )
            
            #名稱有問題
            sql_cmd = "UPDATE Nearbysearch set "
            sql_cmd += "Status = N'-1' "
   
            sql_cmd += " WHERE GUID = '"+ TargetGUID +"'" 
            
            DBConnect.ConnectDB()
            DBConnect.Execute(sql_cmd);
            DBConnect.close()
                               
               

    except TimeoutException as e:
            logger.error("TimeoutException:" +str(featuresIndex))
            try:
                datestr = "test"
                PublicFun.closeWebDriver(datestr,driver)
                time.sleep(1)
                driver = PublicFun.getWebDriver("chrome",True,ShowChrome,True,datestr)
                driver.implicitly_wait(1)  # 隱含等待10秒

                 #名稱有問題
                sql_cmd = "UPDATE Nearbysearch set "
                sql_cmd += "Status = N'-1' "
   
                sql_cmd += " WHERE GUID = '"+ TargetGUID +"'" 
            
                DBConnect.ConnectDB()
                DBConnect.Execute(sql_cmd);
                DBConnect.close()

            except Exception as e3:
                logger.error("featuresIndex4:" +str(featuresIndex))
    except Exception as e2:
        logger.error("featuresIndex2:" +str(featuresIndex))
                

        try:
            datestr = "test"
            PublicFun.closeWebDriver(datestr,driver)
            time.sleep(5)
            driver = PublicFun.getWebDriver("chrome",True,ShowChrome,True,datestr)
            driver.implicitly_wait(1)  # 隱含等待10秒

        except Exception as e3:
                logger.error("featuresIndex3:" +str(featuresIndex))
                


    
ShowChrome = True

if __name__ == '__main__':    
    
    try:

        sys.stdout.reconfigure(encoding='utf-8')

        pattern = r'\d+\.?\d*' # 匹配小数或整数

        print(webdriver.__version__)
    
        chrome_path =  SettingReader.getSetting("base","chrome_path")


        datajson =  SettingReader.getSetting("base","json")

        # 讀取JSON檔案中的資料
        with open(datajson, 'r', encoding='utf-8') as file:
            data = json.load(file)

        selectflag = False

        NextPoint = float( SettingReader.getSetting("base","NextPoint"))
        jumpName = SettingReader.getSetting("base","jumpName")

        sec = False

        featuresIndex = 0

        #SeachModifyDate = SettingReader.getSetting("base","SeachModifyDate")

   
        sql_cmd = "select top 1000000 * from Nearbysearch where Status IS NULL "

        DBConnect = SQLConnect.DBConnect()

        DBConnect.ConnectDB()
        dt = DBConnect.GetDataTable(sql_cmd)
        DBConnect.close()

        for row in  dt:
            print(row.name)
            datestr = "test"
            driver = PublicFun.getWebDriver("chrome",True,ShowChrome,True,datestr)
    
            driver.implicitly_wait(1)  # 隱含等待10秒

            #url = f"https://www.google.com/maps/"
            #driver.get(url)  # 輸入範例網址，交給瀏覽器

            Url = row.url
            GUID = row.GUID
            scanPoints(driver,row.lng,row.lat,row.name,Url,GUID)

            #SettingReader.setSetting("base","SeachModifyDate", str(row.ModifyDate))

        print("結束")
        #url="https://www.google.com/maps/search/tourist_attractions/@-33.9263045,18.5496951,16z/data=!3m1!4b1"
    except Exception as e:
        print("程式內出現無法預測的錯誤:")

    