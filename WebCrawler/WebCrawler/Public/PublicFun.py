import time
import pathlib

repeattimes = 0 #重複次數
#建立ID
def createID():
    import uuid
    return str(uuid.uuid4())

#過濾'字元
def SQLFilter(param):
    if param is None:
        return ""
    return param.replace("'","''")

def valueFilter(param):
    if param is None:
        return ""
    
    param = param.replace("１","1")
    param = param.replace("２","2")
    param = param.replace("３","3")
    param = param.replace("４","4")
    param = param.replace("５","5")
    param = param.replace("６","6")
    param = param.replace("７","7")
    param = param.replace("８","8")
    param = param.replace("９","9")
    param = param.replace("０","0")
    param = param.replace("十一","11")
    param = param.replace("十二","12")
    param = param.replace("十三","13")
    param = param.replace("十四","14")
    param = param.replace("十五","15")
    param = param.replace("十六","16")
    param = param.replace("十七","17")
    param = param.replace("十八","18")
    param = param.replace("十九","19")
    param = param.replace("二十","20")
    param = param.replace("一","1")
    param = param.replace("二","2")
    param = param.replace("三","3")
    param = param.replace("四","4")
    param = param.replace("五","5")
    param = param.replace("六","6")
    param = param.replace("七","7")
    param = param.replace("八","8")
    param = param.replace("九","9")
    param = param.replace("十","10")
    
    return param


#亂數取得停止時間1~10秒
def getSleepTime():
    return getRanNum(1,10)

#取得亂數
def getRanNum(start,end):
    import random
    return random.randint(start-1,end)+start

#取得QueryString
def getQueryString(url,argument):
        querystrings=url.split('?')[1]
        for QueryString in querystrings.split('&'):
            if QueryString.split('=')[0]==argument:
                return QueryString.split('=')[1]
        return ""

#文字轉Json
def StringToJson(text,Default=True):
    import json
    import urllib
    from flask import Flask
    jsonObj={}
    try:
        if(Default):
            data = urllib.parse.unquote(text)
        else:
            data = text
        data2 = data.replace("\"", "")
        data2 = data2.replace("\'", "\"")
        try:
            jsonObj = json.loads(data2)
        except Exception as ex:
            #處理單引號的錯誤
            data = data.replace("\'", "\"")
            split1 = data.split(", ")
            print(split1)
            for split1detail in split1:
                if (split1detail.count("\"") > 4):
                    split2 = split1detail.split(":")
                    for split2detail in split2:
                        if (split2detail.count("\"") > 2):
                            split2detail = split2detail.strip()
                            Reversestring = split2detail[::-1]
                            index = Reversestring.find("\"")
                            split2detailtemp = split2detail[1:len(split2detail)-index-1]
                            Newsplit2detailtemp = split2detailtemp.replace("\"","\'")
                            data= data.replace(split2detailtemp,Newsplit2detailtemp)
                if (split1detail.find("Co.") > -1):
                    #反轉字串
                    split2detailtemp=split1detail
                    Reversestring = split1detail[::-1]
                    index = Reversestring.find("\"")
                    Reversestringtemp = Reversestring[0:index ] +"\'"+Reversestring[index+1:len(Reversestring)]
                    split1detail = Reversestringtemp[::-1]
                    data= data.replace(split2detailtemp,split1detail)
            jsonObj = json.loads(data)
    except Exception as ex:
        jsonObj={}
    
    
    return jsonObj

#取得日期格式By格式
def getNowDateTime(formatstr):
    import datetime
    formatstr = formatstr.upper()
    today = datetime.datetime.now()
    result = ""
    if (formatstr =="YYYY/MM/DD HH:MM:SS"):
        result = str(today.year).zfill(4) +"/"+str(today.month).zfill(2)+"/"+str(today.day).zfill(2)+" "+str(today.hour).zfill(2)+":"+str(today.minute).zfill(2)+":"+str(today.second).zfill(2)
    elif (formatstr =="YYYY/MM/DD"):
        result = str(today.year).zfill(4) +"/"+str(today.month).zfill(2)+"/"+str(today.day).zfill(2)
    elif (formatstr =="HH:MM:SS"):
        result = str(today.hour).zfill(2)+":"+str(today.minute).zfill(2)+":"+str(today.second).zfill(2)
    return result

#取得WebDriver
def getWebDriver(WebDriverType,incognito=True,headless=False,loadPic=True,DataFolderName=""):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import os
    filepath=os.getcwd()
    opts = Options()
    if incognito:
        opts.add_argument("--incognito")  # 使用無痕模式
    if not headless:
        opts.add_argument("--headless") #無介面模式
    if DataFolderName =="":
        DataFolderName=createID()
        
    #DataFolder=os.path.join(getSysTempFolder(),"PyJob",DataFolderName)
    #opts.add_argument("user-data-dir="+DataFolder)  #變更資料儲存位置

   
    #禁止載入圖片模式
    #if not loadPic :
    #    prefs = {"profile.managed_default_content_settings.images": 2}
    #    opts.add_experimental_option("prefs", prefs)
    

    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})
    #全畫面
    opts.add_argument("start-maximized")

    #opts.add_argument('--profile-directory=Default')
    #opts.add_argument('--user-data-dir=C:/Temp/ChromeProfile')

    #opts.add_argument("--disable-gpu")#取消硬體加速 (規避google bug)
    #opts.add_argument("--disable-extensions") #關閉擴充功能
    #opts.add_argument("--no-sandbox")#取消沙盒模式
    #opts.add_argument("--enable-webgl")
    #opts.add_argument("--disable-dev-shm-usage")
   
    WebDriverType=WebDriverType.lower()
    driver = None
    driverVer = None
    if WebDriverType=="chrome":

        print(pathlib.Path(__file__).parent.parent.absolute())

        driverPath = str(pathlib.Path(__file__).parent.parent.absolute()) + "\selenium_driver_chrome\chromedriver.exe"
        #driverPath=os.path.join(filepath,"Program","chromedriver.exe")
        driver=webdriver.Chrome(executable_path=driverPath,chrome_options=opts)

        driverVer = driver.capabilities['browserVersion'][0:3]
        if driverVer =="103":
            driverPath = str(pathlib.Path(__file__).parent.parent.absolute()) + "\selenium_driver_chrome\chromedriver103.exe"
            driver=webdriver.Chrome(executable_path=driverPath,chrome_options=opts)
        if driverVer =="104":
            driverPath = str(pathlib.Path(__file__).parent.parent.absolute()) + "\selenium_driver_chrome\chromedriver104.exe"
            driver=webdriver.Chrome(executable_path=driverPath,chrome_options=opts)
        if driverVer =="105":
            driverPath = str(pathlib.Path(__file__).parent.parent.absolute()) + "\selenium_driver_chrome\chromedriver105.exe"
            driver=webdriver.Chrome(executable_path=driverPath,chrome_options=opts)


    return driver

def getSysTempFolder():
    import os
    return os.environ["TEMP"]

def deleteTempDataFolder(DataFolderName):
    import os
    import shutil
    DataFolder=os.path.join(getSysTempFolder(),"PyJob",DataFolderName)
    try:
        shutil.rmtree(DataFolder)
    except:
        pass

def closeWebDriver(JobID,driver):
    driver.delete_all_cookies()
    driver.close()
    driver.quit()
    deleteTempDataFolder(str(JobID))
    
def execSqlCommand(cnxn,sql_cmd):
    global  repeattimes
    cursor = cnxn.cursor()
    try:
        if repeattimes < 20 :
            print(sql_cmd)
            cursor.execute(sql_cmd)
            cnxn.commit()
        else:
            raise IndexError('execSqlCommand error')
    except:
        repeattimes=repeattimes+1
        time.sleep(5);
        execSqlCommand(cnxn,sql_cmd)
    