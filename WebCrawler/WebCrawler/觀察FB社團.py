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

       
if __name__ == '__main__':    
     
    print(webdriver.__version__)

        
    datestr = "test"

    driver = PublicFun.getWebDriver("chrome",False,True,False,datestr)
    url= "https://www.facebook.com/groups/999413506804235?sorting_setting=CHRONOLOGICAL"
    driver.get(url)  # 輸入範例網址，交給瀏覽器 
    
    time.sleep(12);

    driver.implicitly_wait(10)  # 隱含等待10秒
    Ele = ui.WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "x1yztbdb")))                       
    
    Ele=driver.find_elements_by_class_name("x1yztbdb")
    for i in Ele:
        print(i.text)
    

    PublicFun.closeWebDriver(datestr,driver)
    time.sleep(10);
 