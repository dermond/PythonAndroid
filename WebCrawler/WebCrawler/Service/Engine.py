def Query(dbcon,DataObject,WhereClause=""):
    import Public.PublicFun as PublicFun
    sql=DataObject.QueryStr
    if WhereClause is not None and WhereClause !="":
        WhereClause=" WHERE "+WhereClause
    excuteSQL=sql+WhereClause
    FindRow = dbcon.GetDataTable(excuteSQL)
    if FindRow is not None and len(FindRow)>0:
        DataObject.DataRow=FindRow[0]
    else:
        DataObject.DataRow=[""]*len(DataObject.Fields)
    DataObject.TimeStamp=PublicFun.getNowDateTime("YYYY/MM/DD HH:MM:SS")
    return DataObject

def UpdateData(dbcon,DataObject):
    import Public.PublicFun as PublicFun
    sql=DataObject.QueryStr
    WhereClause=" WHERE 1=1 "
    for key in DataObject.KeyFields:
        WhereClause=WhereClause+" AND "+key+ "='"+DataObject.getData(key)+"'"

    excuteSQL=sql+WhereClause
    FindRow = dbcon.GetDataTable(excuteSQL)

    excuteSQL=""
    NowTime=PublicFun.getNowDateTime("YYYY/MM/DD HH:MM:SS")
    if FindRow is not None and len(FindRow)>0:
        FindRow=FindRow[0]
        DataObject.D_MODIFYTIME=NowTime
        if DataObject.CheckTimeStamp:
            DBTime=FindRow.D_MODIFYTIME
            if DBTime is None or DBTime =="":
                DBTime=FindRow.D_INSERTTIME
            if DBTime >DataObject.TimeStamp:
                raise Exception("The data has been updated by others!")

        excuteSQL="UPDATE "+DataObject.TableName+" SET "
        strField=""
        for Field in DataObject.Fields:
            strField=strField+Field+"=N'"+PublicFun.SQLFilter(DataObject.getData(Field))+"',"
        excuteSQL = excuteSQL+strField.rstrip(',') + WhereClause
    else:
        DataObject.D_INSERTTIME=NowTime
        excuteSQL="INSERT INTO "+DataObject.TableName 
        strField=""
        strValue=""
        for Field in DataObject.Fields:
            strField=strField+Field+","
            strValue=strValue+"N'"+PublicFun.SQLFilter(DataObject.getData(Field))+"',"
        excuteSQL=excuteSQL+"("+strField.rstrip(',')+")VALUES("+strValue.rstrip(',')+")"
    dbcon.Execute(excuteSQL)
    return True
