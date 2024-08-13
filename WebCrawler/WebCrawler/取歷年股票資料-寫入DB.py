# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 22:34:09 2020

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

des_path = r"E:\程式開發\Csv"
temp_Path= r"C:\Users\dermo\Downloads"
FundDetailcmd = ""

def GetFund(csvpath,cnxn , datestr):
    #headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    #https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=20201007&type=ALL
    # 下載股價
    #try:
    #    r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL', headers=headers)
    #except:
    #    time.sleep(10);
    #    r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL', headers=headers)
    # 整理資料，變成表格
    print(csvpath)
    print(datestr)
    try:
        df = pd.read_csv(csvpath,sep = '\r\t' ,encoding='ms950' )
        #break;
    except Exception as e:
        #print('Error')
        print(e.args)
        return
    # 整理一些字串：
    #df = df.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").replace("+", "1").replace("-", "-1"), errors='coerce'))
    
    # 顯示出來
    #df.head()
    #print(datetime.datetime.today())
    #print(df)
    cursor = cnxn.cursor()
    canuse = False
    if (len(df) > 0):
        index = 0
        FundDetailcmd = ""
        for item in df.iterrows(): 
            #print("name=%s" % (row['證券代號']))
            #print(index)
            #print ()
            print(item[1][0].split("\",\"").count("證券代號") )

            #print(shlex.split(item[1][0].replace("\"","") , ","))
            #print(shlex.split(item[1][0].replace("\"","") , ",").count("證券代號") )
            if item[1][0].split("\",\"").count("\"證券代號") > 0 :
                canuse = True
                continue
                
            FundData = item[1][0].split("\",\"")
            if (len(FundData) <= 1):
                continue
            #print(FundData)
            #print(canuse)
            if canuse:
                #print ("item1:" + str(item[1]))
                #print ("item10:" + str(item[1][0]))
                FundID = str(FundData[0]).replace("=\"","").replace("\"","")
                FundName = str(FundData[1])
                sql_cmd = "select * from FundMaster where FundID = '"+FundID+"'"
                print(sql_cmd)
                try:
                    FMflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                except:
                    time.sleep(5);
                    FMflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                #判斷FundMaster是否存在
                if len(FMflag)  == 0:
                    sql_cmd = "INSERT FundMaster (GUID,[FundID],[FundName],[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME])"
                    sql_cmd += " VALUES ("
                    sql_cmd += "'" + str(uuid.uuid1()) + "',"
                    sql_cmd += "'" + FundID + "',"
                    sql_cmd += "'" + FundName + "',"
                    sql_cmd += "'" + str(0) + "',"
                    sql_cmd += "'" + str(datetime.datetime.today()) + "',"
                    sql_cmd += "'" + str(0) + "',"
                    sql_cmd += "'" + str(datetime.datetime.today()) 
                    sql_cmd += "')"
                    #print(sql_cmd)
                    PublicFun.repeattimes = 0
                    PublicFun.execSqlCommand(cnxn,sql_cmd)
                    #try:
                    #    cursor.execute(sql_cmd)
                    #    cnxn.commit()
                    #except:
                    #    time.sleep(5);
                    #    cursor.execute(sql_cmd)
                    #    cnxn.commit()
                    
                
                #判斷FundDetail是否存在
                DealNumberofshares = str(FundData[2])
                DealNumberofentries = str(FundData[3])
                DealAmount = str(FundData[4])
                Openingprice = str(FundData[5])
                Highestprice = str(FundData[6])
                Lowestprice = str(FundData[7])
                Closingprice = str(FundData[8])
                Change = str(FundData[9])
                Pricedifference = str(FundData[10])
                Finallyrevealthepurchaseprice = str(FundData[11])
                Finallyrevealthebuyingvolume = str(FundData[12])
                Finallyrevealthesellingprice = str(FundData[13])
                Finallyrevealthesalesvolume = str(FundData[14])
                PEratio = str(FundData[15].replace("\",",""))
              
                
                sql_cmd = "select * from FundDetail where FundID = '"+FundID+"' AND Date ='"+datestr+"'"  
                print(sql_cmd)
                try:
                    FDflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                except:
                    time.sleep(5);
                    FDflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                    
                #print("FundDetail 可否寫入:" + FDflag)
               
                if len(FDflag)  == 0:
                    print("FundDetail 無資料 寫入")
                    if len(FundDetailcmd) == 0:
                        FundDetailcmd = "INSERT INTO FundDetail ([GUID],[FundID],[Date],[DealNumberofshares],[DealNumberofentries],[DealAmount]"
                        FundDetailcmd += ",[Openingprice],[Highestprice],[Lowestprice],[Closingprice]"
                        FundDetailcmd += ",[Change],[Pricedifference],[Finallyrevealthepurchaseprice],[Finallyrevealthebuyingvolume]"
                        FundDetailcmd += ",[Finallyrevealthesellingprice],[Finallyrevealthesalesvolume],[PEratio]"
                        FundDetailcmd += ",[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME]"
                        FundDetailcmd += " )"
                        
                        
                        FundDetailcmd += " VALUES ("
                        FundDetailcmd += "'" + str(uuid.uuid1()) + "',"
                        FundDetailcmd += "'" + FundID + "',"
                        FundDetailcmd += "'" + datestr + "',"
                        FundDetailcmd += "'" + DealNumberofshares + "',"
                        FundDetailcmd += "'" + DealNumberofentries + "',"
                        FundDetailcmd += "'" + DealAmount + "',"
                        FundDetailcmd += "'" + Openingprice + "',"
                        FundDetailcmd += "'" + Highestprice + "',"
                        FundDetailcmd += "'" + Lowestprice + "',"
                        FundDetailcmd += "'" + Closingprice + "',"
                        FundDetailcmd += "'" + Change + "',"
                        FundDetailcmd += "'" + Pricedifference + "',"
                        FundDetailcmd += "'" + Finallyrevealthepurchaseprice + "',"
                        FundDetailcmd += "'" + Finallyrevealthebuyingvolume + "',"
                        FundDetailcmd += "'" + Finallyrevealthesellingprice + "',"
                        FundDetailcmd += "'" + Finallyrevealthesalesvolume + "',"
                        FundDetailcmd += "'" + PEratio + "',"
                        FundDetailcmd += "'" + str(0) + "',"
                        FundDetailcmd += "'" + str(datetime.datetime.today()) + "',"
                        FundDetailcmd += "'" + str(0) + "',"
                        FundDetailcmd += "'" + str(datetime.datetime.today()) 
                        FundDetailcmd += "')"
                        
                    else:
                        FundDetailcmd += " ,("
                        FundDetailcmd += "'" + str(uuid.uuid1()) + "',"
                        FundDetailcmd += "'" + FundID + "',"
                        FundDetailcmd += "'" + datestr + "',"
                        FundDetailcmd += "'" + DealNumberofshares + "',"
                        FundDetailcmd += "'" + DealNumberofentries + "',"
                        FundDetailcmd += "'" + DealAmount + "',"
                        FundDetailcmd += "'" + Openingprice + "',"
                        FundDetailcmd += "'" + Highestprice + "',"
                        FundDetailcmd += "'" + Lowestprice + "',"
                        FundDetailcmd += "'" + Closingprice + "',"
                        FundDetailcmd += "'" + Change + "',"
                        FundDetailcmd += "'" + Pricedifference + "',"
                        FundDetailcmd += "'" + Finallyrevealthepurchaseprice + "',"
                        FundDetailcmd += "'" + Finallyrevealthebuyingvolume + "',"
                        FundDetailcmd += "'" + Finallyrevealthesellingprice + "',"
                        FundDetailcmd += "'" + Finallyrevealthesalesvolume + "',"
                        FundDetailcmd += "'" + PEratio + "',"
                        FundDetailcmd += "'" + str(0) + "',"
                        FundDetailcmd += "'" + str(datetime.datetime.today()) + "',"
                        FundDetailcmd += "'" + str(0) + "',"
                        FundDetailcmd += "'" + str(datetime.datetime.today()) 
                        FundDetailcmd += "')"
                    
                   # print(sql_cmd)
                    if len(FundDetailcmd) > 10000:
                        print("寫入資料")
                        PublicFun.repeattimes = 0
                        PublicFun.execSqlCommand(cnxn,FundDetailcmd)
                        FundDetailcmd=""
               
                        
                    # sql_cmd = "INSERT FundDetail ([GUID],[FundID],[Date],[DealNumberofshares],[DealNumberofentries],[DealAmount]"
                    # sql_cmd += ",[Openingprice],[Highestprice],[Lowestprice],[Closingprice]"
                    # sql_cmd += ",[Change],[Pricedifference],[Finallyrevealthepurchaseprice],[Finallyrevealthebuyingvolume]"
                    # sql_cmd += ",[Finallyrevealthesellingprice],[Finallyrevealthesalesvolume],[PEratio]"
                    # sql_cmd += ",[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME]"
                    # sql_cmd += " )VALUES ("
                    # sql_cmd += "'" + str(uuid.uuid1()) + "',"
                    # sql_cmd += "'" + FundID + "',"
                    # sql_cmd += "'" + datestr + "',"
                    # sql_cmd += "'" + DealNumberofshares + "',"
                    # sql_cmd += "'" + DealNumberofentries + "',"
                    # sql_cmd += "'" + DealAmount + "',"
                    # sql_cmd += "'" + Openingprice + "',"
                    # sql_cmd += "'" + Highestprice + "',"
                    # sql_cmd += "'" + Lowestprice + "',"
                    # sql_cmd += "'" + Closingprice + "',"
                    # sql_cmd += "'" + Change + "',"
                    # sql_cmd += "'" + Pricedifference + "',"
                    # sql_cmd += "'" + Finallyrevealthepurchaseprice + "',"
                    # sql_cmd += "'" + Finallyrevealthebuyingvolume + "',"
                    # sql_cmd += "'" + Finallyrevealthesellingprice + "',"
                    # sql_cmd += "'" + Finallyrevealthesalesvolume + "',"
                    # sql_cmd += "'" + PEratio + "',"
                    # sql_cmd += "'" + str(0) + "',"
                    # sql_cmd += "'" + str(datetime.datetime.today()) + "',"
                    # sql_cmd += "'" + str(0) + "',"
                    # sql_cmd += "'" + str(datetime.datetime.today()) 
                    # sql_cmd += "')"
                    #print(sql_cmd)
                    # PublicFun.repeattimes = 0
                    # PublicFun.execSqlCommand(cnxn,sql_cmd)
                    #try:

                    #    cursor.execute(sql_cmd)
                    #    cnxn.commit()
                    #except:
                    #    time.sleep(5);
                    #    cursor.execute(sql_cmd)
                    #    cnxn.commit()
                
            index = index + 1
            
        if len(FundDetailcmd) > 0:
            PublicFun.repeattimes = 0
            PublicFun.execSqlCommand(cnxn,FundDetailcmd)
            FundDetailcmd=""
   
def GetTWIndex(csvpath,cnxn , datestr):
    #headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    #https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=20201007&type=ALL
    # 下載股價
    #try:
    #    r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL', headers=headers)
    #except:
    #    time.sleep(10);
    #    r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL', headers=headers)
    # 整理資料，變成表格
    print(csvpath)
    print(datestr)
    try:
        df = pd.read_csv(csvpath,sep = '\r\t' ,encoding='ms950' )
        #break;
    except Exception as e:
        #print('Error')
        print(e.args)
        return
    # 整理一些字串：
    #df = df.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").replace("+", "1").replace("-", "-1"), errors='coerce'))
    
    # 顯示出來
    #df.head()
    #print(datetime.datetime.today())
    #print(df)
    cursor = cnxn.cursor()
    canuse = False
    if (len(df) > 0):
        index = 0
        for item in df.iterrows(): 
            #print("name=%s" % (row['證券代號']))
            #print(index)
            #print ()
            print(item[1][0].split("\",\"").count("指數") )

            #print(shlex.split(item[1][0].replace("\"","") , ","))
            #print(shlex.split(item[1][0].replace("\"","") , ",").count("證券代號") )
            if item[1][0].split("\",\"").count("\"指數") > 0 :
                canuse = True
                continue
            
            if item[1][0].split("\",\"").count("收盤指數") > 0 :
               
                continue
            
            
            if item[1][0].split("\",\"").count("\"成交統計") > 0 :
                
                return
                
            TWIndexData = item[1][0].split("\",\"")
            if (len(TWIndexData) <= 4):
                continue
            print(TWIndexData)
            #print(canuse)
            if canuse:
                
                TWIndexName = str(TWIndexData[0]).replace("=","").replace("\"","")
                sql_cmd = "select * from TWIndexMaster where TWIndexName = '"+TWIndexName+"'"
                try:
                    TWIMflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                except:
                    time.sleep(5);
                    TWIMflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                #判斷FundMaster是否存在
                GUID = str(uuid.uuid1())
                if len(TWIMflag)  == 0:
                    
                    sql_cmd = "INSERT TWIndexMaster (GUID,[TWIndexName],[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME])"
                    sql_cmd += " VALUES ("
                    sql_cmd += "'" + GUID + "',"
                    sql_cmd += "'" + TWIndexName + "',"
                    sql_cmd += "'" + str(0) + "',"
                    sql_cmd += "'" + str(datetime.datetime.today()) + "',"
                    sql_cmd += "'" + str(0) + "',"
                    sql_cmd += "'" + str(datetime.datetime.today()) 
                    sql_cmd += "')"
                    #print(sql_cmd)
                    PublicFun.repeattimes = 0
                    PublicFun.execSqlCommand(cnxn,sql_cmd)
                    #try:
                    #    cursor.execute(sql_cmd)
                    #    cnxn.commit()
                    #except:
                    #    time.sleep(5);
                    #    cursor.execute(sql_cmd)
                    #    cnxn.commit()
                    
                #判斷FundDetail是否存在
                Closingindex = str(TWIndexData[1]).replace("\"","")
                Upsanddowns = str(TWIndexData[2]).replace("\"","")
                Changepoints = str(TWIndexData[3]).replace("\"","")
                Percentagechange = str(TWIndexData[4]).replace("\"","")
                Specialtreatment = str(TWIndexData[5]).replace("\"","")
                Mark = ""
               
              
                
                sql_cmd = "select * from TWIndexDetail where ParentGUID = '"+GUID+"' AND Date ='"+datestr+"'"  
                
                try:
                    TWIDflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                except:
                    time.sleep(5);
                    TWIDflag = pd.read_sql(sql=sql_cmd, con=cnxn)
                    
                if len(TWIDflag)  == 0:
                    sql_cmd = "INSERT TWIndexDetail ([GUID],[ParentGUID],[Date],[Closingindex],[Upsanddowns],[Changepoints]"
                    sql_cmd += ",[Percentagechange],[Specialtreatment],[Mark]"
                    sql_cmd += ",[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME]"
                    sql_cmd += " )VALUES ("
                    sql_cmd += "'" + str(uuid.uuid1()) + "',"
                    sql_cmd += "'" + GUID + "',"
                    sql_cmd += "'" + datestr + "',"
                    sql_cmd += "'" + Closingindex + "',"
                    sql_cmd += "'" + Upsanddowns + "',"
                    sql_cmd += "'" + Changepoints + "',"
                    sql_cmd += "'" + Percentagechange + "',"
                    sql_cmd += "'" + Specialtreatment + "',"
                    sql_cmd += "'" + Mark + "',"
                    sql_cmd += "'" + str(0) + "',"
                    sql_cmd += "'" + str(datetime.datetime.today()) + "',"
                    sql_cmd += "'" + str(0) + "',"
                    sql_cmd += "'" + str(datetime.datetime.today()) 
                    sql_cmd += "')"
                    print(sql_cmd)
                    PublicFun.repeattimes = 0
                    PublicFun.execSqlCommand(cnxn,sql_cmd)
                    #try:

                    #    cursor.execute(sql_cmd)
                    #    cnxn.commit()
                    #except:
                    #    time.sleep(5);
                    #    cursor.execute(sql_cmd)
                    #    cnxn.commit()
                
            index = index + 1
           
def DownLoadAllFund(datestr,cnxn):
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    #https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=20201007&type=ALL
    # 下載股價
    try:
        r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL', headers=headers)
    except:
        time.sleep(10);
        r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL', headers=headers)
    # 整理資料，變成表格
    print(r.text)
    print(r.encoding)
    #i = 0
    
    #for l in r.text.split("\n"):
        #print(l)
        
        #if (l.find("#") ):
            #print("Find")
            #print(l)
            
        #i+= 1
    if (len(r.text) == 0):
        return
    #print(StringIO(r.text.replace("=", "")))
    #print(StringIO(r.text.replace("=", "").replace("n", "")[195]))
    #df = pd.read_csv(StringIO(r.text.replace("=", "")),header=["證券代號" in l for l in r.text.split("\n")].index(True)-1)
    #df = pd.read_csv(StringIO(r.text), sep='delimiter', header=None)
    df = pd.read_csv(StringIO(r.text), sep='\t', header=None)
    
    path = os.path.join(des_path , datestr+'.csv') 
    print(path)
    
        
    df.to_csv(path, encoding='ms950')
    
def DownLoadAllFundforselenium(datestr):
    csvpath =  os.path.join(des_path , 'MI_INDEX_ALL_' + datestr + '.csv')
    print(csvpath)
    if not os.path.isfile(csvpath):
        driver = PublicFun.getWebDriver("chrome",False,True,False,datestr)
        
        path = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL'
        print(path)
        driver.get(path)  # 輸入範例網址，交給瀏覽器 
        time.sleep(5);
        PublicFun.closeWebDriver(datestr,driver)
        moveDownloadFileToTempFolder()
  
def ParsingCsv():
    cnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=DMS;UID=DMS;PWD=DMS")
    
    allFileList = os.listdir(des_path)
    for file in allFileList:
        print(os.path.join(des_path , file))
        GetFund(os.path.join(des_path , file ),cnxn , file.replace("MI_INDEX_ALL_","").replace(".csv","") )
        GetTWIndex(os.path.join(des_path , file ),cnxn , file.replace("MI_INDEX_ALL_","").replace(".csv","") )
        shutil.copyfile(os.path.join(des_path , file), os.path.join(des_path ,'Processed', file))
        os.remove(os.path.join(des_path , file))
        #break;
    
def moveDownloadFileToTempFolder():
    
    if not os.path.isdir(des_path):  #如果資料夾不存在就建立
        os.mkdir(des_path)
    
    
    allFileList = os.listdir(temp_Path)
    for file in allFileList:
        #(file)
        oldfile = os.path.join(temp_Path , file)
        newfile = os.path.join(des_path , file)
        size = os.path.getsize(oldfile)
        #print(size)
        #print(oldfile)
        #print(file.find("MI_INDEX_ALL_"))
        if size != 0 and file.find("MI_INDEX_ALL_") >= 0:
            shutil.copyfile(oldfile, newfile)
            os.remove(oldfile)
    
if __name__ == '__main__':          
    #datestr = '20200916'
    #datestr = time.strftime("%Y-%m-%d", time.localtime()).replace("-","")
    cnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=DMS;UID=sa;PWD=13000")
    chrome_path = "E:\程式開發\selenium_driver_chrome\chromedriver.exe" #chromedriver.exe執行檔所存在的路徑
    #driver = PublicFun.getWebDriver("chrome",chromedriverPath)
    #driver = webdriver.Chrome(chrome_path)
    #172 173
    #44 100
    for i in range(0,0):
        datestr = (datetime.datetime(2020,12,7,0,0,0)+datetime.timedelta(days=i)).strftime("%Y%m%d")
        #datestr = (datetime.datetime.now()+datetime.timedelta(days=0-i)).strftime("%Y%m%d")
        print (i)
        print (datestr)
        #print ((datetime.datetime.now()+datetime.timedelta(days=-1)).strftime("%Y%m%d"))
        try:
            DownLoadAllFundforselenium(datestr)
            #DownLoadAllFund(datestr,cnxn)
            #GetFund(datestr,cnxn)
            #GetTWIndex(datestr,driver)
        except Exception as e:
            #print('Error')
            print(e.args)
            #error_class = e.__class__.__name__ #取得錯誤類型
            #detail = e.args[0] #取得詳細內容
            #cl, exc, tb = sys.exc_info() #取得Call Stack
            #lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            #fileName = lastCallStack[0] #取得發生的檔案名稱
            #lineNum = lastCallStack[1] #取得發生的行號
            #funcName = lastCallStack[2] #取得發生的函數名稱
            #errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            #print(errMsg)
            time.sleep(10);
            #GetFund(datestr,cnxn)
    ParsingCsv()
        

          
#sql_cmd = "select * from FundMaster"
#df = pd.read_sql(sql=sql_cmd, con=cnxn)
#print (len(df))