# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 12:23:27 2021

@author: dermo
"""
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
import Service.SQLConnect as SQLConnect
from selenium.webdriver.support.ui import WebDriverWait
#from shapely.geometry import Polygon, Point

temp_Path= r"C:\Users\dermo\Downloads"

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

def extract_lat_lng_from_google_maps_url(url):
    # 正則表達式匹配緯度和經度
    pattern = r'/@([-\d.]+),([-\d.]+)'
    match = re.search(pattern, url)

    if match:
        lat, lng = match.groups()
        return float(lat), float(lng)
    else:
        pattern = r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)"

        match = re.search(pattern, url)
        if match:
            lat, lng = match.groups()
            return float(lat), float(lng)
        else:
            print("錯誤Url取經緯度:" + url)
            return None, None

def execute_name(name):
   if name in name_cache:  # 檢查名稱是否存在於快取中
        return True
   else:
        name_cache[name] = True  # 寫入名稱到快取中
        return False

       


if __name__ == '__main__':    
     
    pattern = r'\d+\.?\d*' # 匹配小数或整数

    print(webdriver.__version__)
    
    chrome_path =  SettingReader.getSetting("base","chrome_path")

    datestr = "test"
    driver = PublicFun.getWebDriver("chrome",False,True,False,datestr)
    
    driver.implicitly_wait(2)  # 隱含等待10秒
    

  

    ## 讀取JSON檔案中的資料
    #with open('data/taiwan.json', 'r', encoding='utf-8') as file:
    #    data = json.load(file)

    #selectflag = False

    NextPoint = float( SettingReader.getSetting("base","NextPoint"))

    #全球
    #t1 = '-57.999, -179.999'
    #t2 = '71, 180'

    #Temp
    #t1 = '26.385560, 120.465086'
    #t2 = '26.350955, 120.513923'

    #台灣
    #t1 = '22.681290, 121.460480'
    #t2 = '22.629488, 121.513008'

    #台灣
    #t1 = '25.321670, 120.147841'
    #t2 = '21.842754, 121.910648'

    #南非
    #t1 = '-22.230946, 14.426631'
    #t2 = '-34.900558, 32.848865'
    t1 = '37.147182, 137.526617'
    t2 = '35.7914677,139.020757'

    t1 = SettingReader.getSetting("base","t1")
    t2 = SettingReader.getSetting("base","t2")


    seleniumCount = 0

    lat = float(t1.split(",")[0].strip())
    lng = float(t1.split(",")[1].strip())

    Maxlat = float(t2.split(",")[0].strip())
    Maxlng = float(t2.split(",")[1].strip())

    if (lat > Maxlat):
        tmp = lat
        lat = Maxlat
        Maxlat = tmp

    tmp = lng
    if (lng > Maxlng):
       
        lng = Maxlng
        Maxlng = tmp
        tmp = lng
        
    dlat, dlng = square_point(Maxlat,Maxlng,NextPoint)
    lat = lat - dlat - dlat
    lng = lng  - dlng -  dlng

    Maxlat = Maxlat + dlat+ dlat
    Maxlng = Maxlng + dlng+ dlng

    while lat <= Maxlat :
        lng = tmp
         
        while lng <= Maxlng :
            #if not is_point_inside_polygon(lng, lat, points):

            #    dlat, dlng = square_point(lat,lng,NextPoint)
            #    lng= lng + dlng
            #    continue
            try:
                    
                lat = round(lat, 7)
                lng = round(lng, 7)

                #print (lat,lng)
                keyword = 'service'
                keyword = 'food'
                keyword = 'restaurant'
                #keywords = ['restaurant', 'tourist_attraction','dessert','scenic_spot']
                keywords = SettingReader.getList("base","keywords")


                zoom = str(16)
                    
                if NextPoint <= 1:
                    zoom = str(16)
                elif NextPoint > 1 and NextPoint <= 2:
                    zoom = str(15)
                elif NextPoint > 2 and NextPoint <= 5:
                    zoom = str(14)
                elif NextPoint > 5 and NextPoint <= 10:
                    zoom = str(13)
                elif NextPoint > 10 and NextPoint <= 20:
                    zoom = str(12)
                elif NextPoint > 20 :
                    zoom = str(11)


                for keyword in keywords:
                    #keyword = 'tourist_attraction'
                    try:
                        driver.execute_cdp_cmd(
                            "Browser.grantPermissions",
                            {
                                "origin": "https://www.openstreetmap.org/",
                                "permissions": ["geolocation"],
                            },
                        )


                        Map_coordinates = dict({
                            "latitude": lat,
                            "longitude": lng,
                            "accuracy": 100
                            })
                        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", Map_coordinates)
                        driver.execute_cdp_cmd("Page.setGeolocationOverride", Map_coordinates)
                 
                        url = f"https://www.google.com/maps/search/{keyword}/@{lat},{lng},"+zoom+f"z/"

                    

                        #print(url)
                        driver.get(url)  # 輸入範例網址，交給瀏覽器 

                        seleniumCount = seleniumCount + 1

                        #搶Focus
                        #driver.switch_to.window(driver.window_handles[0])

                        #time.sleep(1)

                        # 查找附近的店家信息
                        places = driver.find_elements(By.CSS_SELECTOR,".Nv2PK")

                        # 等待元素出現
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]'))
                        )

                        pane = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
                        parent_element = pane.find_element(By.XPATH,"..")
                
                        endindex = 0

                        scrollbarDown= float(SettingReader.getSetting("base","scrollbarDown"))
                        start_time5 = time.time()
                        while (pane.text.find("你已看完所有搜尋結果") == -1 or pane.text.find("没有其他结果") == -1)and parent_element.text.find("項結果") == -1  and endindex < scrollbarDown : 
        
                            # 等待元素出現
                            element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]'))
                            )

                            # 評論分頁下滑

                            pane = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
                            parent_element = pane.find_element(By.XPATH,"..")

                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
                
                            #time.sleep(1)

                            if (pane.text.find("找不到任何結果") > -1):
                                break;
                            if (pane.text.find("没有其他结果") > -1):
                                break;
                            if (pane.text.find("地图无法找到") > -1):
                                break;

                        
                            endindex = endindex + 1

                        # 查找附近的店家信息
                        places = driver.find_elements(By.CSS_SELECTOR,".Nv2PK")

                        # 輸出附近的店家信息
           
                        for place in places:
                            try:
                                isCloseing = False
                                name = place.find_element(By.CSS_SELECTOR,".NrDZNb").text

                                #if (name =='Jun-Ine'):
                                #     print(name)
                                W4Efsds = place.find_elements(By.CSS_SELECTOR,".W4Efsd")
                                ratings = W4Efsds[0].text.split("(")[0].split("\x00")[0].strip()
                                result = re.findall(pattern, ratings)

                                if result:
                                    ratings = str(float(result[0]))
                                    #print(number)
                                else:
                                    ratings = str(0)

                                user_total_ratings =  W4Efsds[0].text.replace(",","").replace("\x00","").strip()

                                if ( len(user_total_ratings.split("(")) >= 2 ):
                                    user_total_ratings = user_total_ratings.split("(")[1].split(")")[0]
                                else:
                                    continue

                                for W4Efsd in W4Efsds:
                                    if (W4Efsd.text.find("永久停業") > -1):
                                        isCloseing = True
                                types = W4Efsds[1].text.split("·")[0].split("\n")[0].strip()

                                if (types.find("營業時間") > -1):
                                    types=''

                                href = place.find_element(By.CSS_SELECTOR,".hfpxzc").get_attribute("href")

                                newlat, newlng = extract_lat_lng_from_google_maps_url(href)

                                if execute_name(str(name) + str(newlat) + str(newlng)):
                              
                                    continue
                                #print(name, ratings,user_total_ratings,types)
                                if (str(newlat) == 'None'):
                                    continue
 
                                DBConnect = SQLConnect.DBConnect()

                                #確定下載了 才會記錄
                                sql_cmd = "exec Sp_Nearbysearch_Set_Ins "
                                sql_cmd += "N'" + name.replace("'","''") + "',"
                                sql_cmd += "N'" + str(newlat) +','+ str(newlng) + "',"
                                sql_cmd += "'" + str(ratings) + "',"
                                sql_cmd += "'" + str(user_total_ratings) + "',"
                                sql_cmd += "N'" + keyword+'@@'+ types  + "'," 
                                sql_cmd += "'" + str(newlat) + "',"
                                sql_cmd += "'" + str(newlng) + "',"
                                sql_cmd += "'" + '' + "',"
                                sql_cmd += "'" + href.replace("'","''") + "',"
                                if (isCloseing):
                                    sql_cmd += "'1',"
                                else:
                                    sql_cmd += "'0',"
                                #sql_cmd += "'" + str(datetime.datetime.today())  + "',"
                                sql_cmd += "''" 
                                #print(sql_cmd)

                                #PublicFun.repeattimes = 0
                                DBConnect.ConnectDB()
                                DBConnect.Execute(sql_cmd);
                                DBConnect.close()

                            except Exception as e:
                                print(name,e)
                                continue

                    except Exception as e:
                        print(e)


            except Exception as e:
                print('有錯誤')
    
            dlat, dlng = square_point(lat,lng,NextPoint)
            lng= lng + dlng

            if (seleniumCount > 100):
                    

                datestr = "test"
                PublicFun.closeWebDriver(datestr,driver)
                time.sleep(5)
                driver = PublicFun.getWebDriver("chrome",False,True,False,datestr)
                driver.implicitly_wait(0)  # 隱含等待10秒
                seleniumCount = 0    
                    
               


        dlat, dlng = square_point(lat,lng,NextPoint)
        lat= lat + dlat

    print("結束")
    #url="https://www.google.com/maps/search/tourist_attractions/@-33.9263045,18.5496951,16z/data=!3m1!4b1"
    

    