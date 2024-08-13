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

def scanPoints(driver,lat,lon):
       
    # Set the threshold for memory usage warning (80%)
    #memory_usage_threshold = 80
    #memory_usage_threshold = SettingReader.getSetting("base","memory_usage_threshold")
    

    latlngflag = False
    min_lat =lat
    max_lat  =lat
    min_lon = lon
    max_lon = lon

    
    lng = float(min_lat)
    lat = float(min_lon)

    Maxlng = float(max_lat)
    Maxlat = float(max_lon)

    
    
    NextPoint = float( SettingReader.getSetting("base","NextPoint"))
    memoryNextPoint  = NextPoint
    dlat, dlng = square_point(Maxlat,Maxlng,NextPoint)
    lat = lat #- dlat 
    lng = lng  #- dlng 
    Maxlat = Maxlat #+ dlat
    Maxlng = Maxlng #+ dlng


    if (lat > Maxlat):
        tmp = lat
        lat = Maxlat
        Maxlat = tmp

    tmp = lng
    if (lng > Maxlng):
       
        lng = Maxlng
        Maxlng = tmp
        tmp = lng

    jumpLatLng = SettingReader.getList("base","jumpLatLng")

    seleniumCount = 100
    temp = SettingReader.getSetting("base","seleniumCount")
    if temp == '':
        seleniumCount = 100
    else:

        seleniumCount  =  float(temp)

    continuous = 0 #連續地點的數量
    while lat <= Maxlat :
        lng = tmp
         
        while lng <= Maxlng :

            
            #if not is_point_inside_polygon(lng, lat, points):

            ##    #print(f"Point ({lat}, {lng}) is inside the polygon.")
            #    dlat, dlng = square_point(lat,lng,NextPoint)
            #    lng= lng + dlng
            #    continue
            try:
                placecount= 0

                start_time = time.time()
                start_time7 = time.time()
                lat = round(lat, 7)
                lng = round(lng, 7)


                logger.info("lat lng:" +str(lat) + "," + str(lng) )
                
                #print (lat,lng)
                keyword = 'service'
                keyword = 'food'
                keyword = 'restaurant'
                #keyword = 'tourist_attraction'
                keywords = ['tourist_attraction']

                keywords = SettingReader.getList("base","keywords")

                zoom = str(16)
                
                if NextPoint <= 1:
                    zoom = str(15)
                elif NextPoint > 1 and NextPoint <= 2:
                    zoom = str(14)
                elif NextPoint > 2 and NextPoint <= 5:
                    zoom = str(13)
                elif NextPoint > 5 and NextPoint <= 10:
                    zoom = str(12)
                elif NextPoint > 10 and NextPoint <= 20:
                    zoom = str(11)
                elif NextPoint > 20 :
                    zoom = str(10)

               
                

                for keyword in keywords:

                    #memory_usage_percent = get_memory_usage_percentage()
                    #print(f"memory_usage_percent: {memory_usage_percent} %")
                    #print(f"memory_usage_threshold: {memory_usage_threshold} %")

                    driver.delete_all_cookies()
                    driver.refresh()

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

                    #time.sleep(2)
                    try:
                         # 等待元素出現
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]'))
                        )
                        pane = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]')
                        if pane.text.find("地圖找不到") > -1 :
                            continue
                    except Exception as e:
                        endindex = 0


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

                    end_time6 = time.time()
                    # 计算执行时间
                    execution_time = end_time6 - start_time5

                    # 输出执行时间
                    #print("程序执行时间为: {}秒".format(execution_time))
                    #logger.info("scrollbar:{}".format(execution_time))

                    # 查找附近的店家信息
                    places = driver.find_elements(By.CSS_SELECTOR,".Nv2PK")

                    # 輸出附近的店家信息
                   
                    if (len(places) == 0):

                        print("單筆資料")
                        QyI6Nb = ui.WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME , "QyI6Nb")))  
                        #QyI6Nb =  driver.find_element(By.CLASS_NAME,".QyI6Nb")
                        QyI6Nb.click()
                        time.sleep(2)
                        try:
                            isCloseing = False
                            name = driver.find_element(By.CSS_SELECTOR,".DUwDvf").text

                            if name == '':
                                continue
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
                                continue

                            for W4Efsd in W4Efsds:
                                if (W4Efsd.text.find("永久停業") > -1):
                                    isCloseing = True
                            types =driver.find_element(By.CSS_SELECTOR,".DkEaL").text.split("·")[0].split("\n")[0].strip()
                             
                            if (types.find("營業時間") > -1):
                                types=''
                           


                            href = driver.current_url
                            if (len(href.split("!8m2!3d")) == 1):
                               
                                continue
                            else:
                                newlat = href.split("!8m2!3d")[1].split("!16")[0].split("!4d")[0]
                                newlng = href.split("!8m2!3d")[1].split("!16")[0].split("!4d")[1]

                            if execute_name(str(name) + str(newlat) + str(newlng)):
                              
                                continue


                            #print(name, ratings,user_total_ratings,types)

                            DBConnect = SQLConnect.DBConnect()

                            #確定下載了 才會記錄
                            sql_cmd = "exec Sp_Nearbysearch_Set_Ins "
                            sql_cmd += "N'" + name.replace("'","''") + "',"
                            sql_cmd += "N'" + newlat +','+ newlng + "',"
                            sql_cmd += "'" + ratings + "',"
                            sql_cmd += "'" + user_total_ratings + "',"
                            sql_cmd += "N'" + keyword+'@@'+ types  + "'," 
                            sql_cmd += "'" + newlat + "',"
                            sql_cmd += "'" + newlng + "',"
                            sql_cmd += "'" + '' + "',"
                            sql_cmd += "'" + href.replace("'","''") + "',"
                            if (isCloseing):
                                sql_cmd += "'1',"
                            else:
                                sql_cmd += "'0',"
                            #sql_cmd += "'" + str(datetime.datetime.today())  + "',"
                            sql_cmd += "''" 
                            #print(sql_cmd)
                            #print(name.replace("'","''") + " featuresIndex1:" +str(featuresIndex)  )
                            logger.info(name.replace("'","''") + " featuresIndex1:" +str(featuresIndex) + " " + str(datetime.datetime.today()))
                            #PublicFun.repeattimes = 0
                            
                            start_time3 = time.time()
                            DBConnect.ConnectDB()
                            DBConnect.Execute(sql_cmd);
                            DBConnect.close()
                            end_time4 = time.time()
                            # 计算执行时间
                            execution_time = end_time4 - start_time3

                            # 输出执行时间
                            print("程序执行时间为: {}秒".format(execution_time))
                           
                                

                        except Exception as e:
                           

                            #print(name,e)
                            #print("異常發生在程式碼行數：", traceback.extract_tb(e.__traceback__)[-1].lineno)
                            #logger.error("異常發生在程式碼行數：", traceback.extract_tb(e.__traceback__)[-1].lineno)

                            logger.error("featuresIndex1:" +str(featuresIndex) )
                            time.sleep(5)
                               
                            #continue
                        else:
        
                            placecount = placecount + 1
                           
                            continue
                        continue



                    for place in places:
                        start_time1 = time.time()
                        max_attempts = 3  # 最大嘗試次數
                        attempts = 0      # 目前嘗試次數

                        while attempts < max_attempts:
                            try:
                                isCloseing = False
                                name = place.find_element(By.CSS_SELECTOR,".NrDZNb").text

                                if name == '':
                                    attempts = max_attempts
                                    continue
                                W4Efsds = place.find_elements(By.CSS_SELECTOR,".W4Efsd")
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
                                    attempts = max_attempts
                                    continue

                                for W4Efsd in W4Efsds:
                                    if (W4Efsd.text.find("永久停業") > -1):
                                        isCloseing = True
                                types = W4Efsds[1].text.split("·")[0].split("\n")[0].strip()

                                if (types.find("營業時間") > -1):
                                    types=''
                           


                                href = place.find_element(By.CSS_SELECTOR,".hfpxzc").get_attribute("href")
                                if (len(href.split("!8m2!3d")) == 1):
                                    attempts = max_attempts
                                    continue
                                else:
                                    newlat = href.split("!8m2!3d")[1].split("!16")[0].split("!4d")[0]
                                    newlng = href.split("!8m2!3d")[1].split("!16")[0].split("!4d")[1]

                                if execute_name(str(name) + str(newlat) + str(newlng)):
                                    attempts = max_attempts
                                    continue


                                #print(name, ratings,user_total_ratings,types)

                                DBConnect = SQLConnect.DBConnect()

                                #確定下載了 才會記錄
                                sql_cmd = "exec Sp_Nearbysearch_Set_Ins "
                                sql_cmd += "N'" + name.replace("'","''") + "',"
                                sql_cmd += "N'" + newlat +','+ newlng + "',"
                                sql_cmd += "'" + ratings + "',"
                                sql_cmd += "'" + user_total_ratings + "',"
                                sql_cmd += "N'" + keyword+'@@'+ types  + "'," 
                                sql_cmd += "'" + newlat + "',"
                                sql_cmd += "'" + newlng + "',"
                                sql_cmd += "'" + '' + "',"
                                sql_cmd += "'" + href.replace("'","''") + "',"
                                if (isCloseing):
                                    sql_cmd += "'1',"
                                else:
                                    sql_cmd += "'0',"
                                #sql_cmd += "'" + str(datetime.datetime.today())  + "',"
                                sql_cmd += "''" 
                                #print(sql_cmd)
                                #print(name.replace("'","''") + " featuresIndex1:" +str(featuresIndex)  )
                                logger.info(name.replace("'","''") + " featuresIndex1:" +str(featuresIndex) + " " + str(datetime.datetime.today()))
                                #PublicFun.repeattimes = 0
                                start_time3 = time.time()
                                DBConnect.ConnectDB()
                                DBConnect.Execute(sql_cmd);
                                DBConnect.close()
                                end_time4 = time.time()
                                # 计算执行时间
                                execution_time = end_time4 - start_time3

                                # 输出执行时间
                                print("程序执行时间为: {}秒".format(execution_time))
                                #logger.info("DB:{}秒".format(execution_time))
                                attempts = max_attempts
                                

                            except Exception as e:
                                # 嘗試次數加一
                                attempts += 1

                                #print(name,e)
                                #print("異常發生在程式碼行數：", traceback.extract_tb(e.__traceback__)[-1].lineno)
                                #logger.error("異常發生在程式碼行數：", traceback.extract_tb(e.__traceback__)[-1].lineno)

                                logger.error("featuresIndex1:" +str(featuresIndex) )
                                time.sleep(5)
                               
                                #continue
                            else:
                                # 如果沒有發生錯誤，則跳出while迴圈
                                attempts = max_attempts
                                placecount = placecount + 1
                                end_time2 = time.time()
                                # 计算执行时间
                                execution_time = end_time2 - start_time1

                                continue
                       

                        # 输出执行时间
                        #print("程序执行时间为: {}秒".format(execution_time))
                        #logger.info("place:{}".format(execution_time))
                if (seleniumCount > 100):
                    
                    end_time8 = time.time()
                    # 计算执行时间
                    execution_time = end_time8 - start_time7

                    # 输出执行时间
                    #print("程序执行时间为: {}秒".format(execution_time))
                    logger.info("seleniumCount:{}".format(execution_time))

                    datestr = "test"
                    PublicFun.closeWebDriver(datestr,driver)
                    time.sleep(5)
                    driver = PublicFun.getWebDriver("chrome",True,ShowChrome,True,datestr)
                    driver.implicitly_wait(0)  # 隱含等待10秒
                    seleniumCount = 0    
                    
                    start_time7 = time.time()
                
               

                end_time = time.time()

                # 计算执行时间
                execution_time = end_time - start_time

                SettingReader.setSetting("base","jumpLatLng", str(lat) + "," + str(lng))
                # 输出执行时间
                #print("程序执行时间为: {}秒".format(execution_time))
               
                logger.info("latlng:{}".format(execution_time))
            except TimeoutException as e:
                 logger.error("TimeoutException:" +str(featuresIndex))
                 try:
                    datestr = "test"
                    PublicFun.closeWebDriver(datestr,driver)
                    time.sleep(5)
                    driver = PublicFun.getWebDriver("chrome",True,ShowChrome,True,datestr)
                    driver.implicitly_wait(1)  # 隱含等待10秒

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
                

            if (placecount < 2):
                #continuous = continuous + 1
                fastNextPoint = NextPoint + memoryNextPoint
                NextPoint = fastNextPoint
                
            else:
                NextPoint = memoryNextPoint


            dlat, dlng = square_point(lat,lng,NextPoint)
            lng= lng + dlng

        NextPoint = memoryNextPoint       

        
        dlat, dlng = square_point(lat,lng,NextPoint)
        lat= lat + dlat


def truncate_to_three_decimals(num):
    """截斷數字到小數點後三位"""
    return int(num * 1000) / 1000

def fetch_nearbysearch_data(name):
    """從資料庫獲取資料"""
    sql_cmd = "SELECT * FROM Nearbysearch WHERE name = N'{}'".format(name)
    DBConnect = SQLConnect.DBConnect()
    DBConnect.ConnectDB()
    data = DBConnect.GetDataTable(sql_cmd)
    DBConnect.close()
    return data

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

        SeachModifyDate = SettingReader.getSetting("base","SeachModifyDate")

   
        sql_cmd =  "SELECT Top 100 A.name, A.lat, A.lng , A.GUID"
        sql_cmd += " FROM Nearbysearch A"
        sql_cmd += " CROSS JOIN Nearbysearch B"
        sql_cmd += " WHERE A.name = B.name"
        sql_cmd += " AND ABS(TRY_CAST(A.lat AS decimal(18,7)) - TRY_CAST(B.lat AS decimal(18,7))) <= 0.001"
        sql_cmd += " AND ABS(TRY_CAST(A.lng AS decimal(18,7)) - TRY_CAST(B.lng AS decimal(18,7))) <= 0.001"
        sql_cmd += " AND (TRY_CAST(A.lat AS decimal(18,7)) <> TRY_CAST(B.lat AS decimal(18,7)) "
        sql_cmd += "     OR TRY_CAST(A.lng AS decimal(18,7)) <> TRY_CAST(B.lng AS decimal(18,7)))"
        sql_cmd += " AND A.GUID <> B.GUID;"

        DBConnect = SQLConnect.DBConnect()

        DBConnect.ConnectDB()
        dt = DBConnect.GetDataTable(sql_cmd)
        DBConnect.close()

        for row in  dt:
            print(row.name+ ":" + row.GUID)

            name = row.name
            GUID = row.GUID

            sql_cmd = "select * from Nearbysearch WHERE name = N'"+ name +"'"

            DBConnect = SQLConnect.DBConnect()

            DBConnect.ConnectDB()
            Nearbysearchdt = DBConnect.GetDataTable(sql_cmd)
            DBConnect.close()



            datestr = "test"
            driver = PublicFun.getWebDriver("chrome",True,ShowChrome,True,datestr)
    
            driver.implicitly_wait(1)  # 隱含等待10秒

            #url = f"https://www.google.com/maps/"
            #driver.get(url)  # 輸入範例網址，交給瀏覽器

            scanPoints(driver,row.lng,row.lat)

            SettingReader.setSetting("base","SeachModifyDate", str(row.ModifyDate))
        #print(data,data["features"])
        #print("總共有幾筆資料:" + str(len(data["features"])))
        #logger.info("總共有幾筆資料:" + str(len(data["features"])))
        #for feature in data["features"]:
        #    #print(feature["geometry"]["coordinates"])

        #    featuresIndex=featuresIndex+1
        #    name = ""
        #    if "name" in feature['properties']:
        #        print(feature['properties']['name'])
        #        name = feature['properties']['name']
        #    if "NAME_CIAWF" in feature['properties']:
        #        print(feature['properties']['NAME_CIAWF'])
        #        name = feature['properties']['NAME_CIAWF']
       

        #    logger.info(name)
        #    if (jumpName == ""):
        #         selectflag = True
        #    else:
        #       if not name is None:
        #            if (name.replace('\n', '').replace('\r', '') == jumpName):
        #                selectflag = True

        #       if (str(featuresIndex) == str(jumpName)):
        #                selectflag = True

            
       
        #    if (not selectflag):
        #         continue

       

        #    #print("featuresIndex:" +str(featuresIndex) )
        #    logger.info("featuresIndex:" +str(featuresIndex))
        #    for Area in  feature["geometry"]["coordinates"]:
          
           
        #        if len(Area[0]) > 2:
        #            for Area2 in  Area:
        #                #print(len(Area2))

        #                scanPoints(driver,Area2,sec)
                   

                    
        #        else:
                
    
        #            scanPoints(driver,Area,sec)

        #    sec = True
               
              

           




        print("結束")
        #url="https://www.google.com/maps/search/tourist_attractions/@-33.9263045,18.5496951,16z/data=!3m1!4b1"
    except Exception as e:
        print("程式內出現無法預測的錯誤:")

    