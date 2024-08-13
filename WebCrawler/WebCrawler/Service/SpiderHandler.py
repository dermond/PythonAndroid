#Get下載區的目前檔案數量
def getDownloadListCount(path):
    import os
    result = 0
    try:
        result = int(len([lists for lists in os.listdir(path) if os.path.isfile(os.path.join(path, lists))]))
    except Exception as ex:
        result = 0
    return result

