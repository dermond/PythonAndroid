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
import Service.SQLConnect as SQLConnect

temp_Path= r"C:\Users\dermo\Downloads"

       

def  GetSeachStr(TextStr):
    if TextStr.find("桃乃木かな") > 0 :
        return True
    if TextStr.find("西宮ゆめ") > 0 :
        return True
    if TextStr.find("椎名そら") > 0 :
        return True
    if TextStr.find("夢乃あいか") > 0 :
        return True
    if TextStr.find("楓カレン") > 0 :
        return True
    if TextStr.find("愛瀬るか") > 0 :
        return True
    if TextStr.find("水卜さくら") > 0 :
        return True
    if TextStr.find("沙月芽衣") > 0 :
        return True
    if TextStr.find("さつき芽衣") > 0 :
        return True
    if TextStr.find("三宮つばき") > 0 :
        return True
    if TextStr.find("桜空もも") > 0 :
        return True
    if TextStr.find("碓氷れん") > 0 :
        return True
    if TextStr.find("楪カレン") > 0 :
        return True

    return False


if __name__ == '__main__':    
     
    print(webdriver.__version__)

    #清除多餘的檔案
    allFileList = os.listdir(temp_Path)
    for file in allFileList:
        print(file)

        if os.path.isdir(str(temp_Path)+"/"+str(file)):
            continue
        elif os.path.isfile(str(temp_Path)+"/"+str(file)):
             print(str(temp_Path)+"/"+str(file))
        else:
            continue


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

    DBConnect = SQLConnect.DBConnect()
    
    try:
        #登入帳號
        UseridEle = ui.WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))                       
    
        UseridEle=driver.find_element_by_name("username")
        UseridEle.send_keys('dermond')
        
        #登入密碼
        UseridEle=driver.find_element_by_name("password")
        UseridEle.send_keys('19840522')

        
        #按下登陸
        OKEle=driver.find_element_by_name("loginsubmit")
        ActionChains(driver).click(OKEle).perform()
        #time.sleep(1)
    except Exception as ex:
        print("無須登入")
    
    for page in range(5,70):
    #尋找元素
        print("page:"+ str(page))
        driver.switch_to.window(driver.window_handles[0])
        driver.get('https://twed2k.org/forumdisplay.php?fid=33&page='+str(page))  # 輸入範例網址，交給瀏覽器 
       
        try:
            Ele = ui.WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "altbg2")))                       
    
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
                    
                    if int(viewcount) < 180:
                        print("人數不夠 不下載")
                        if not GetSeachStr(i.text) :

                            continueflag = True
                            
                    if i.text.find("NTR") > -1 and int(viewcount) > 160:
                        continueflag = False
                    
                    if i.text.find("中出") > -1 and int(viewcount) > 160:
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
                        DBConnect.ConnectDB()
                        DLflag = DBConnect.GetDataTable(sql_cmd)
                        DBConnect.close()
                        print(DLflag)
                        #DLflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                        if len(DLflag)  != 0:
                            print("此檔案下載過")
                            continue
                    except Exception as ex:
                        print(ex)
                    #DLflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                    
                    
                    print("1")
                    
                    #換分頁
                    driver.switch_to.window(driver.window_handles[1])
                    #driver.implicitly_wait(10)
                    try:
                        Ele2=driver.find_elements_by_css_selector("a")
                        print("2")
                        #Ele2 = ui.WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a")))
                        print("3")
                       
                        for j in Ele2:
                            
                            if j.text.find("http") > -1 :
                                print(j.text)
                                driver.get(j.text)  # 輸入範例網址，交給瀏覽器 
                                
                                path = r"C:\Users\dermo\Downloads"
                                filecount = SpiderHandler.getDownloadListCount(path)

                                
                                #driver.switch_to.window(driver.window_handles[1])
                                Submit = ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Submit")))
                                ActionChains(driver).click(Submit).perform()
                                newfilecount = SpiderHandler.getDownloadListCount(path)
                                if newfilecount > filecount:
                                    break

                                driver.switch_to.window(driver.window_handles[1])
                                Submit = ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Submit")))
                                ActionChains(driver).click(Submit).perform()
                                newfilecount = SpiderHandler.getDownloadListCount(path)
                                if newfilecount > filecount:
                                    break

                                driver.switch_to.window(driver.window_handles[1])
                                Submit = ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Submit")))
                                ActionChains(driver).click(Submit).perform()
                                newfilecount = SpiderHandler.getDownloadListCount(path)
                                if newfilecount > filecount:
                                    break
                        
                                #raise IndexError('尋找Submit錯誤')

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

                        #PublicFun.repeattimes = 0
                        DBConnect.ConnectDB()
                        DBConnect.Execute(sql_cmd);
                        DBConnect.close()
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

        if os.path.isdir(str(temp_Path)+"/"+str(file)):
            continue
        elif os.path.isfile(str(temp_Path)+"/"+str(file)):
             print(str(temp_Path)+"/"+str(file))
        else:
            continue

        if file.find("(1)") > -1 :
            os.remove(str(temp_Path)+"/"+str(file))
        if file.find("(2)") > -1 :
            os.remove(str(temp_Path)+"/"+str(file))
            
        
 