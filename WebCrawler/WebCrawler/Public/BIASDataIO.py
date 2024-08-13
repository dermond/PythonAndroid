def findOption(dbcon,OptionName):
    import Public.PublicFun as PublicFun
    sql=("SELECT GUID FROM OPTAAA WHERE OPTAAA001=N'"+PublicFun.SQLFilter(OptionName) +"'")
    OptionGUID= dbcon.GetDataTable(sql)
    if OptionGUID is not None and len(OptionGUID)>0:
        return OptionGUID[0].GUID
    return ""

def insertOption(dbcon,OptionName,RelGUID = None):
    import Public.PublicFun as PublicFun
    GUID=PublicFun.createID()
    sql=("INSERT INTO [dbo].[OPTAAA]([GUID],[OPTAAA001],[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME])"
    +"VALUES('"+GUID+"',N'"+PublicFun.SQLFilter(OptionName) +"','System','" + PublicFun.getNowDateTime("YYYY/MM/DD HH:MM:SS") + "','','')")
    dbcon.Execute(sql)
    if RelGUID is not None:
        sql=("INSERT INTO [dbo].[OPTAAB]([GUID],[OPTAAB001],[OPTAAB002],[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME])"
        +"VALUES('"+PublicFun.createID()+"','"+RelGUID+"','"+GUID+"','System','" + PublicFun.getNowDateTime("YYYY/MM/DD HH:MM:SS") + "','','')")
        dbcon.Execute(sql)
    return GUID

def findCompany(dbcon,CompanysName):
    import Public.PublicFun as PublicFun
    sql=("SELECT GUID FROM Companys WHERE Companys003=N'"+PublicFun.SQLFilter(CompanysName) +"'")
    CompanysGUID= dbcon.GetDataTable(sql)
    if CompanysGUID is not None and len(CompanysGUID)>0:
        return CompanysGUID[0].GUID
    return ""

def CheckMappingList(dbcon,MapType,Value):
    import Public.PublicFun as PublicFun
    if ( MapType== "CompanyName"): 
        sql=("SELECT TOP 1 MAPAAA003 FROM MAPAAA WHERE MAPAAA001='"+MapType+"' AND MAPAAA002=N'"+PublicFun.SQLFilter(Value)+"'")
    else:
        sql=("SELECT TOP 1 MAPAAA003 FROM MAPAAA WHERE MAPAAA001='"+MapType+"' AND MAPAAA002=N'"+Value+"'")
    return dbcon.GetDataTable(sql)

def insertMappingList(dbcon,MapType,Value,RelValue):
    import Public.PublicFun as PublicFun
    GUID=PublicFun.createID()
    sql=("INSERT INTO [dbo].[MAPAAA]([GUID],[MAPAAA001],[MAPAAA002],[MAPAAA003],[D_INSERTUSER],[D_INSERTTIME],[D_MODIFYUSER],[D_MODIFYTIME])"
    +"VALUES('"+GUID+"',N'"+PublicFun.SQLFilter(MapType) +"',N'"+PublicFun.SQLFilter(Value)+"',N'"+PublicFun.SQLFilter(RelValue)+"','System','" + PublicFun.getNowDateTime("YYYY/MM/DD HH:MM:SS") + "','','')")
    dbcon.Execute(sql)
    return GUID

def CheckCompanyMappingList(dbcon,CompanyName,CompanyGUID=None,NewCompanyGUID=True):
    import Public.PublicFun as PublicFun
    MAPCompanyGUID = CheckMappingList(dbcon,"CompanyName",CompanyName)
    if MAPCompanyGUID is None or len(MAPCompanyGUID)==0:
        if CompanyGUID is None:
            CompanyGUID = findCompany(dbcon,CompanyName)
            if (CompanyGUID is None or CompanyGUID == ""):
                if (NewCompanyGUID):
                    CompanyGUID=PublicFun.createID()
                else:
                    CompanyGUID=""
        insertMappingList(dbcon,"CompanyName",CompanyName,CompanyGUID)
    else:
        CompanyGUID=MAPCompanyGUID[0].MAPAAA003
    return CompanyGUID
