def IdentifyVerifyCode(imgPath,getPublicSetting=True):
    import base64
    import os

    import Public.SettingReader as SettingReader
    encoded_string=""
    with open(imgPath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    
    import requests
    req=requests.session()
    header={
        'content-type': 'raw;text/plain;charset=UTF-8;application/json'
    }
    req.headers.update(header)

    data="{'pic':"+str(encoded_string).lstrip('b')+", 'lang':'"+SettingReader.getPublicSetting("Identify","lang")+"'}"
    if (getPublicSetting):
        IdentifyServer=SettingReader.getPublicSetting("Identify","server")
    else:
        IdentifyServer=SettingReader.getSetting("Identify","server")
    
    res=req.post(IdentifyServer,data=data)
    import json
    result=json.loads(res.text)
    status=result["status"]
    if status != "-1":
        VerifyCode=result["result"].replace('\\','').replace('\n','')
        imgName=VerifyCode+"_"+result["serialNubmer"]+".png"
        os.rename(imgPath,os.path.join(os.getcwd(),"tempFolder",imgName))
        return imgName
    raise Exception("驗證碼取得失敗")