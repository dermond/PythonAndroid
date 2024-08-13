def getSetting(secName,keyName):
    from configparser import RawConfigParser
    import os
    filepath=os.getcwd()
    settingfilePath=os.path.join(filepath,"setting.ini")
    parser=RawConfigParser()
    parser.read(settingfilePath, encoding = 'utf8')
    return parser.get(secName,keyName)

def getPublicSetting(secName,keyName):
    from configparser import RawConfigParser
    import os
    #EDIT BY cjshie 因為共用的setting.ini會與這個檔案放在同目錄, 所以直接取目前的目錄即可, 這樣主要執行的.py就可以放在任意位置
    filepath = os.path.dirname(os.path.realpath(__file__))
    settingfilePath=os.path.join(filepath,"setting.ini")
    parser=RawConfigParser()
    parser.read(settingfilePath, encoding = 'utf8')
    return parser.get(secName,keyName)