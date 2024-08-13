def ExecuteJobs(threadCount,ConditionQueue):
    import os
    import Public.LogHandler as LogHandler
    import Public.QueueIO as QueueIO
    import json
    import urllib
    
    while ConditionQueue.qsize() > 0:
        thisQueue=None
        try:
            thisQueue=ConditionQueue.get()
            LogHandler.writeMsg(thisQueue.SystemName+"剩餘執行數量："+str(ConditionQueue.qsize()))
            jsonData  = json.dumps(str(thisQueue.Param))
            jsonData = urllib.parse.quote(jsonData)
            Queuestr =  r"chcp 65001 && cd /d "+thisQueue.Path +"&&"+ r"python "+thisQueue.Path+thisQueue.Files
            Queuestr += " " + str(threadCount)
            Queuestr += " %s"% (jsonData)
            f=os.popen(Queuestr)
            ExecuteMsg = f.readlines()
            if (str(ExecuteMsg).find("母體請重置此Queue") > -1):
                if (str(ExecuteMsg).find("HTTPSConnectionPool") > -1 ):
                    thisQueue.QueueType= "Excute"
                    QueueIO.addQueueJob(thisQueue)
                else:
                    thisQueue.QueueType= "Error"
                    QueueIO.addQueueJob(thisQueue)
            
                
        except Exception as ex:
            thisQueue.QueueType= "Error"
            QueueIO.addQueueJob(thisQueue)
            QueueIO.writeDBMsg("執行續失敗執行:" + thisQueue.SystemName + " ex:"+str(ex))
