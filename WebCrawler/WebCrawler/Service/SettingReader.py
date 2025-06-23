def getSetting(secName,keyName):
    from configparser import RawConfigParser
    import os
    import chardet

    result = ""
    try:
        filepath=os.getcwd()
        settingfilePath=os.path.join(filepath,"setting.ini")
        parser=RawConfigParser()

        
        # 使用 chardet 檢測文件編碼
        with open(settingfilePath, 'rb') as file:
            encoding = chardet.detect(file.read())['encoding']


        parser.read(settingfilePath,  encoding=encoding)
        result = parser.get(secName,keyName)
    except Exception as ex:
        print(ex)
        result = ""
    return result

def getList(secName,keyName):
    from configparser import RawConfigParser
    import os
    import chardet
    result = []
    try:
        filepath=os.getcwd()
        settingfilePath=os.path.join(filepath,"setting.ini")
        parser=RawConfigParser()

        # 使用 chardet 檢測文件編碼
        with open(settingfilePath, 'rb') as file:
            encoding = chardet.detect(file.read())['encoding']

        parser.read(settingfilePath, encoding=encoding)
        result = parser.get(secName,keyName).split(',')
    except Exception as ex:
        print(ex)
        result = []
    return result


def getPublicSetting(secName,keyName):
    from configparser import RawConfigParser
    import os
    import chardet
    #EDIT BY cjshie 因為共用的setting.ini會與這個檔案放在同目錄, 所以直接取目前的目錄即可, 這樣主要執行的.py就可以放在任意位置
    filepath = os.path.dirname(os.path.realpath(__file__))
    settingfilePath=os.path.join(filepath,"setting.ini")
    parser=RawConfigParser()

     # 使用 chardet 檢測文件編碼
    with open(settingfilePath, 'rb') as file:
        encoding = chardet.detect(file.read())['encoding']

    parser.read(settingfilePath, encoding=encoding)
    return parser.get(secName,keyName)

def setSetting(secName, keyName, value):
    from configparser import RawConfigParser
    import os
    import chardet

    result = ""
    try:
        filepath = os.getcwd()
        settingfilePath = os.path.join(filepath, "setting.ini")
        parser = RawConfigParser()

        # 檢查檔案是否存在，若不存在就建立空檔
        if not os.path.exists(settingfilePath):
            with open(settingfilePath, 'w', encoding='utf-8') as f:
                f.write("")  # 建立空白檔案

        # 使用 chardet 偵測編碼
        with open(settingfilePath, 'rb') as file:
            encoding = chardet.detect(file.read())['encoding'] or 'utf-8'

        parser.read(settingfilePath, encoding=encoding)

        # 如果 section 不存在，則新增
        if not parser.has_section(secName):
            parser.add_section(secName)

        # 設定指定 key 的值
        parser.set(secName, keyName, value)

        # 寫入設定
        with open(settingfilePath, 'w', encoding=encoding) as configfile:
            parser.write(configfile)

    except Exception as ex:
        result = ex

    return result