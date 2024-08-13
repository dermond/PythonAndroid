class QueueJob():
    def __init__(self):
        self.SystemName= ""
        self.QueueType=""
        self.Path = ""
        self.Files= ""
        self.Param= None

def getQueue(SystemName,QueueType):
    import queue
    resultQueue=queue.Queue()
    sql=(
        "SELECT * FROM JobQueue WHERE SystemName=N'"+SystemName+"' AND QueueType=N'"+QueueType+"' order by D_INSERTTIME" 
    )
    dbcon=getQueueDBConnect()
    dt=dbcon.GetDataTable(sql)
    for row in dt:
        tmpJob=QueueJob()
        tmpJob.SystemName=row.SystemName
        tmpJob.QueueType=row.QueueType
        tmpJob.Path=row.Path
        tmpJob.Files=row.Files
        tmpJob.Param=row.Param
        resultQueue.put(tmpJob)

    sql=(
        "delete FROM JobQueue WHERE SystemName=N'"+SystemName+"' AND QueueType=N'"+QueueType+"'" 
    )
    dbcon.Execute(sql)
    dbcon.close()
    return resultQueue

def addQueueJob(QueueJobObj):
    addQueue(QueueJobObj.SystemName,QueueJobObj.QueueType,QueueJobObj.Path,QueueJobObj.Files,QueueJobObj.Param)

def addQueue(SystemName,QueueType,Path,Files,Param):
    import Public.PublicFun as PublicFun
    
    GUID=PublicFun.createID()
    jsonData = str(Param)
    D_INSERTTIME = PublicFun.getNowDateTime("YYYY/MM/DD HH:MM:SS")
    dbcon=getQueueDBConnect()
    sql=(
        "INSERT INTO [dbo].[JobQueue]([GUID],[SystemName],[QueueType],[Path],[Files],[Param],[D_INSERTTIME])"+
        "VALUES('"+GUID+"',N'" + PublicFun.SQLFilter(SystemName) + "',N'"+PublicFun.SQLFilter(QueueType)+"',N'"+PublicFun.SQLFilter(Path)+"',N'"+PublicFun.SQLFilter(str(Files))+"',N'" + PublicFun.SQLFilter(str(jsonData))+"','" + str(D_INSERTTIME) + "')"
    )
    dbcon.Execute(sql)
    dbcon.close()

def setParameter(Key,Value,JsonObj=None):
    import json
    if JsonObj is None:
        JsonObj=json.loads("{}")
    if Key in JsonObj:
        raise Exception("Key重複")
    JsonObj[Key]=Value
    return JsonObj

def writeDBMsg(msg):
    import Public.PublicFun as PublicFun
    import Public.LogHandler as LogHandler
    
    dbcon=getQueueDBConnect()
    sql=(
    "INSERT INTO [dbo].[LogMsg]([GUID],[Message],[D_INSERTTIME])"+
    "VALUES('"+PublicFun.createID()+"',N'"+PublicFun.SQLFilter(msg)+"','" + PublicFun.getNowDateTime("YYYY/MM/DD HH:MM:SS") + "')"
    )
    try:
        dbcon.Execute(sql)
    except:
        msg="writeDBMsg失敗："+msg
    LogHandler.writeMsg(msg)
    dbcon.close()

def getQueueDBConnect():
    import Public.SQLConnect as SQLConnect
    DBConnect=SQLConnect.DBConnect("QueueConnect",publicSetting=True)
    DBConnect.ConnectDB()
    return DBConnect
    