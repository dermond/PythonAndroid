# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 21:32:34 2021

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
import Public.PublicFun as PublicFun
from selenium.webdriver.common.action_chains import ActionChains


if __name__ == '__main__':   
    chrome_path = "E:\程式開發\selenium_driver_chrome\chromedriver.exe" #chromedriver.exe執行檔所存在的路徑
    #driver = PublicFun.getWebDriver("chrome",chromedriverPath)
    #driver = webdriver.Chrome(chrome_path)
    datestr = "test"
    driver = PublicFun.getWebDriver("chrome",False,True,False,datestr)
    driver.get('https://bigsale.tmall.com/wow/a/act/haiwaifenzu/tmc/31953/4764/wupr?spm=a2141.241046-cn.banner_middle.d_mcard.260b6f11QyllVV&wh_pid=main-246439&disableNav=YES&status_bar_transparent=true')  # 輸入範例網址，交給瀏覽器 
    




    #PublicFun.closeWebDriver(datestr,driver)    