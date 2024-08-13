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
from selenium.webdriver.common.keys import Keys

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

if __name__ == '__main__':    
     
    print(webdriver.__version__)
    
    chrome_path =  SettingReader.getSetting("base","chrome_path")

    datestr = "test"
    driver = PublicFun.getWebDriver("chrome",False,True,False,datestr)
    
    driver.implicitly_wait(2)  # 隱含等待10秒

    DBConnect = SQLConnect.DBConnect()

    sql_cmd = "SELECT * FROM [DMS].[dbo].[Nearbysearch]  where url is null"

    DBConnect.ConnectDB()
    urlnulls = DBConnect.GetDataTable(sql_cmd)

    DBConnect.close()
    for urlnull in urlnulls:
        print(urlnull.location)
   
        t1 = urlnull.location
        t2 = urlnull.location
        #t1 = '-22.230946, 14.426631'
        #t2 = '-34.900558, 32.848865'

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

       # while lat <= Maxlat :

       #     lng = tmp
       #     while lng <= Maxlng :

        try:

            print (lat,lng)

            lat = round(lat, 7)
            lng = round(lng, 7)

            keyword = 'food'
            keyword = 'restaurant'
            keyword = 'tourist_attraction'
            keyword = 'lodging'
            keyword = ''
            #keyword = urlnull.types.split("@@")[0]
                
            Map_coordinates = dict({
                "latitude": lat,
                "longitude": lng,
                "accuracy": 100
                })
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", Map_coordinates)

            url = f"https://www.google.com/maps/search/{keyword}/@{lat},{lng},16z/"

                

            print(url)
            driver.get(url)  # 輸入範例網址，交給瀏覽器 
    
            time.sleep(5)

            Ele = ui.WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))                       
    
            Ele=driver.find_element_by_id("searchboxinput")
            Ele.send_keys(urlnull.name)
            time.sleep(1)
            Ele.send_keys(Keys.ENTER)

            time.sleep(5)


            ## 查找附近的店家信息
            #places = driver.find_elements_by_css_selector(".Nv2PK")
                        
            #spec = 2
            #if (len(driver.find_elements_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div')) == 4):
            #    spec = 3
            #else:
            #    spec = 2


            #pane = driver.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div['+str(spec)+']/div[1]')
            ##pane = driver.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
            #parent_element = pane.find_element_by_xpath("..")
                
            #endindex = 0

            #while pane.text.find("你已看完所有搜尋結果") == -1 and parent_element.text.find("項結果") == -1  and endindex < 20 :
        
            #    # 評論分頁下滑
            #    pane = driver.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div['+str(spec)+']/div[1]')
            #    #pane = driver.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
            #    parent_element = pane.find_element_by_xpath("..")

            #    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
                
            #    #time.sleep(1)

            #    if (pane.text.find("找不到任何結果") > -1):
            #        break;

            #    endindex = endindex + 1

            ## 查找附近的店家信息
            #places = driver.find_elements_by_css_selector(".Nv2PK")

            ## 輸出附近的店家信息
           
            #for place in places:
            #    try:
            isCloseing = False
            tmp = driver.find_elements_by_css_selector(".DUwDvf")
            if (len(tmp) == 0):
                #查出多筆資料
                places = driver.find_elements_by_css_selector(".Nv2PK")
                for place in places:
                    try:
                        isCloseing = False
                        name = place.find_element_by_css_selector(".NrDZNb").text
                        W4Efsds = place.find_elements_by_css_selector(".W4Efsd")
                        ratings = W4Efsds[0].text.split("(")[0].strip()

                        if ( len(W4Efsds[0].text.split("(")) >= 2 ):
                             user_total_ratings = W4Efsds[0].text.split("(")[1].split(")")[0].replace(",","").strip()
                        else:
                            continue

                        for W4Efsd in W4Efsds:
                            if (W4Efsd.text.find("永久停業") > -1):
                                isCloseing = True
                        types = W4Efsds[1].text.split("·")[0].split("\n")[0].strip()

                        href = place.find_element_by_css_selector(".hfpxzc").get_attribute("href")

                        newlat = href.split("!8m2!3d")[1].split("!16")[0].split("!4d")[0]
                        newlng = href.split("!8m2!3d")[1].split("!16")[0].split("!4d")[1]

                        print(name, ratings,user_total_ratings,types)

                        DBConnect = SQLConnect.DBConnect()

                        #確定下載了 才會記錄
                        sql_cmd = "exec Sp_Nearbysearch_Set_Ins "
                        sql_cmd += "N'" + name.replace("'","''") + "',"
                        sql_cmd += "N'" + newlat +','+ newlng + "',"
                        sql_cmd += "'" + ratings + "',"
                        sql_cmd += "'" + user_total_ratings + "',"
                        sql_cmd += "'" + keyword+'@@'+ types  + "'," 
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
                        print(sql_cmd)

                        #PublicFun.repeattimes = 0
                        DBConnect.ConnectDB()
                        DBConnect.Execute(sql_cmd);
                        DBConnect.close()

                    except Exception as e:
                        print(name)
                        continue

                continue
            name = driver.find_element_by_css_selector(".DUwDvf").text
            W4Efsds = driver.find_elements_by_css_selector(".F7nice")
            if (len(W4Efsds) == 0):
                continue

            ratings = W4Efsds[0].text.split("\n")[0].strip()
            user_total_ratings = W4Efsds[0].text.split("\n")[1].split("則")[0].replace(",","").strip()
                    
            for W4Efsd in W4Efsds:
                if (W4Efsd.text.find("永久停業") > -1):
                    isCloseing = True
                            
            types = driver.find_element_by_css_selector(".skqShb").find_elements_by_css_selector(".fontBodyMedium")
            for type in types:
                if (type.text.strip().find("評論") > -1 or type.text.strip().find(")") > -1):
                    types = 'tourist_attraction'
                    #keyword = 'tourist_attraction'
                else:
                    types = type.text.strip()
                    #keyword = type.text.strip()

            # 獲取當前網頁的 URL 字串
            current_url = driver.current_url

            href = current_url

            #newlat = current_url.split(",")[0].split("@")[1]
            #newlng = current_url.split(",")[1]
            newlat = str(lat)
            newlng = str(lng)

            print(name, ratings,user_total_ratings,types)

                        

            #確定下載了 才會記錄
            sql_cmd = "exec Sp_Nearbysearch_Set_Ins "
            sql_cmd += "N'" + name.replace("'","''") + "',"
            sql_cmd += "N'" + newlat +','+ newlng + "',"
            sql_cmd += "'" + ratings + "',"
            sql_cmd += "'" + user_total_ratings + "',"
            sql_cmd += "'" + keyword.replace("'","''")+'@@'+ types.replace("'","''")  + "'," 
            sql_cmd += "'" + newlat + "',"
            sql_cmd += "'" + newlng + "',"
            sql_cmd += "'" + '' + "',"
            sql_cmd += "'" + href.replace("'","''") + "',"
            if isCloseing :
                sql_cmd += "'1',"
            else:
                sql_cmd += "'0',"
            #sql_cmd += "'" + str(datetime.datetime.today())  + "',"
            sql_cmd += "''" 
            print(sql_cmd)

            #PublicFun.repeattimes = 0
            DBConnect.ConnectDB()
            DBConnect.Execute(sql_cmd);
            DBConnect.close()

    #            except Exception as e:
    #                print(name)
    #                continue

    #        if (parent_element.text.find("項結果") > -1):
    #            aaa = "";

        except Exception as e:
            print('有錯誤')
            continue

            #    dlat, dlng = square_point(lat,lng,0.2)
            #    lng= lng + dlng

            #dlat, dlng = square_point(lat,lng,0.2)
            #lat= lat + dlat


    #url="https://www.google.com/maps/search/tourist_attractions/@-33.9263045,18.5496951,16z/data=!3m1!4b1"
    
