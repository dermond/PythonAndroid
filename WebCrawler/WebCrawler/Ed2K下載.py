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

temp_Path= r"C:\Users\dermo\Downloads"

    
if __name__ == '__main__':    
    
    #清除多餘的檔案
    allFileList = os.listdir(temp_Path)
    for file in allFileList:
        print(file)

        if file.find("(1)") > -1 :
            os.remove(str(temp_Path)+"/"+str(file))
        if file.find("(2)") > -1 :
            os.remove(str(temp_Path)+"/"+str(file))
            
       
        
    
    chrome_path =  SettingReader.getSetting("base","chrome_path")
    #driver = PublicFun.getWebDriver("chrome",chromedriverPath)
    #driver = webdriver.Chrome(chrome_path)
    datestr = "test"
    driver = PublicFun.getWebDriver("chrome",False,True,False,datestr)
    url=SettingReader.getSetting("base","url") + "1"
    print(url)
    driver.get(url)  # 輸入範例網址，交給瀏覽器 
    
    driver.implicitly_wait(10)  # 隱含等待10秒

    cnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=DMS;UID=sa;PWD=13000")
    
    try:
        #登入帳號
        UseridEle=driver.find_element_by_name("username")
        UseridEle.send_keys('dermond')
        
        #登入密碼
        UseridEle=driver.find_element_by_name("password")
        UseridEle.send_keys('19840522')

        
        #按下登陸
        OKEle=driver.find_element_by_name("loginsubmit")
        ActionChains(driver).click(OKEle).perform()
        #time.sleep(1)
    except:
        print("無須登入")
    
    for page in range(5,70):
    #尋找元素
        print("page:"+ str(page))
        driver.switch_to.window(driver.window_handles[0])
        driver.get('https://twed2k.org/forumdisplay.php?fid=33&page='+str(page))  # 輸入範例網址，交給瀏覽器 
       
        try:
            Ele=driver.find_elements_by_class_name("altbg2")
            


            for i in Ele:
                
                #Trim 清左右空格
                # print(i)
                # print(i.text.find("[BT]"))
                #換分頁
 
               
                while len(driver.window_handles) > 1:
                    print("handles len:" +str(len(driver.window_handles)))
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                    #time.sleep(1)
                    
               
                driver.switch_to.window(driver.window_handles[0])
                    
                if i.text.find("[BT]") > -1 :
                    print("BT")
                    print(i.text)
                    
                    filename = i.text
                    #print("上一層文字")
                    tr = i.find_element_by_xpath("..").text
                    # with open("F:\Output.txt", "w",encoding="utf-8") as text_file:
                    #     text_file.write("Purchase Amount: %s" % tr)
    
                    count=0
                    for trtd in tr.splitlines():
                        
                        if (count == 2):
                            viewcount = trtd.split(" ")[2]
                            
                        if (count == 3):
                            trtime = trtd 
                        #print("tr td:"+ trtd)
                        count +=1
                        
                    print(viewcount)
                    #print(trtime)
                    
                    #觀看人數 要大於160 才需要下載
                    continueflag = False
                    
                    if int(viewcount) < 200:
                        print("人數不夠 不下載")
                        if i.text.find("桃乃木かな") == -1 \
                            and i.text.find("西宮ゆめ") == -1 \
                                and i.text.find("椎名そら") == -1 \
                                    and i.text.find("夢乃あいか") == -1 \
                                        and i.text.find("楓カレン") == -1 \
                                            and i.text.find("愛瀬るか") == -1 \
                                                and i.text.find("水卜さくら") == -1 \
                                                    and i.text.find("沙月芽衣") == -1 \
                                                        and i.text.find("さつき芽衣") == -1 \
                                                            and i.text.find("三宮つばき") == -1 \
                                                                and i.text.find("桜空もも") == -1 \
                                                                    and i.text.find("碓氷れん") == -1:
                                                   
                                                       
                            continueflag = True
                            
                    if i.text.find("NTR") > -1 and int(viewcount) > 100:
                        continueflag = False
                    
                    if i.text.find("中出") > -1 and int(viewcount) > 100:
                        continueflag = False
                        
                        
                    if i.text.find("素人") > -1 :
                        continueflag = True
                    
                    if continueflag == True:
                        continue
                    
                    
                    diff = datetime.datetime.strptime(trtime,"%Y-%m-%d %I:%M %p")
                  
                    i.find_element_by_tag_name("a").click()
                    
                    
                    sql_cmd = "select * from DownLoadList where DLName = N'"+filename + "'"
                    print(sql_cmd)
                    try:
                        DLflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                    except:
                        time.sleep(5);
                    
                    DLflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                    
                    if len(DLflag)  != 0:
                        print("此檔案下載過")
                        continue
                        
                    
                    #換分頁
                    driver.switch_to.window(driver.window_handles[1])
                    #driver.implicitly_wait(10)
                    time.sleep(1)
                    try:
                        Ele2=driver.find_elements_by_css_selector("a")
                        for j in Ele2:
                            if j.text.find("http") > -1 :
                                print(j.text)
                                driver.get(j.text)  # 輸入範例網址，交給瀏覽器 
                                
                                path = r"C:\Users\dermo\Downloads"
                                filecount = SpiderHandler.getDownloadListCount(path)
                                
                                
                                #time.sleep(4)
                                #等5秒按下
                                print("1")
                                time.sleep(1)
                                #Submit = ui.WebDriverWait(driver,20).until(EC.presence_of_element_located(By.NAME ,"Submit"))
                                #driver.switch_to.window(driver.window_handles[1])
                                driver.switch_to.window(driver.window_handles[1])
                                Submit = ui.WebDriverWait(driver,20).until(lambda x: x.find_element_by_name("Submit"))
                                ActionChains(driver).click(Submit).perform()

                                driver.switch_to.window(driver.window_handles[1])
                                Submit = ui.WebDriverWait(driver,20).until(lambda x: x.find_element_by_name("Submit"))
                                ActionChains(driver).click(Submit).perform()

                                driver.switch_to.window(driver.window_handles[1])
                                Submit = ui.WebDriverWait(driver,20).until(lambda x: x.find_element_by_name("Submit"))
                                ActionChains(driver).click(Submit).perform()


                                newfilecount = SpiderHandler.getDownloadListCount(path)
                                if newfilecount > filecount:
                                    
                                    break
                        
                                raise IndexError('尋找Submit錯誤')

                        #確定下載了 才會記錄
                        sql_cmd = "INSERT DownLoadList ([GUID],[DLName]"
                        sql_cmd += ",[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME]"
                        sql_cmd += " )VALUES ("
                        sql_cmd += "'" + str(uuid.uuid1()) + "',"
                        sql_cmd += "N'" + filename + "',"
                        sql_cmd += "'" + str(0) + "',"
                        sql_cmd += "'" + str(datetime.datetime.today()) + "',"
                        sql_cmd += "'" + str(0) + "',"
                        sql_cmd += "'" + str(datetime.datetime.today()) 
                        sql_cmd += "')"
                        print(sql_cmd)
                        PublicFun.repeattimes = 0
                        #PublicFun.execSqlCommand(cnxn,sql_cmd)
                    except Exception as e:
                        print(e)
                        print("Error1")
                        #time.sleep(1)
                    

        except Exception as e:
            print(e)
            print("Error2")
            #time.sleep(1)
    
    
        
    PublicFun.closeWebDriver(datestr,driver)
    
    #清除多餘的檔案
    allFileList = os.listdir(temp_Path)
    for file in allFileList:
        print(file)

        if file.find("(1)") > -1 :
            os.remove(str(temp_Path)+"/"+str(file))
        if file.find("(2)") > -1 :
            os.remove(str(temp_Path)+"/"+str(file))
            
        
        