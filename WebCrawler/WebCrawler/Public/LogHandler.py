import Public.PublicFun as PublicFun
import Public.SQLConnect as SQLConnect

def writeMsg(msg):
    import time 
    msg=str(time.strftime('%Y%m%d%H%M%S'))+":"+msg+"\n"
    print(msg, end='')

def writethreadMsg(threadCount,msg):
    writeMsg("執行續"+str(threadCount)+" "+msg)
    
def writeDBMsg(JobName,Param,msg,dbcon=None):
    import Public.PublicFun as PublicFun
    if dbcon is None:
        dbcon=SQLConnect.DBConnect(publicSetting=True)
        dbcon.ConnectDB()
        writeDBMsg(JobName,Param,msg,dbcon)
        dbcon.close()
    else:
        try:
            sql=("INSERT INTO [dbo].[LogMsg]([GUID],[JOB],[Param],[Message],[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME])"
            +"VALUES('"+PublicFun.createID()+"',N'"+PublicFun.SQLFilter(JobName) +"',N'"+PublicFun.SQLFilter(str(Param)) +"',N'"+PublicFun.SQLFilter(str(msg)) +"',N'"+PublicFun.SQLFilter(JobName) +"','" + PublicFun.getNowDateTime("YYYY/MM/DD HH:MM:SS") + "','','')")
            dbcon.Execute(sql)
            writeMsg(str(msg))
        except Exception as ex:
            writeMsg("寫入資料庫失敗:"+ex)
    