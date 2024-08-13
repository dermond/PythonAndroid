
import os
import Service.SQLConnect as SQLConnect
import pandas as pd
import xlsxwriter
import Service.ExcelHandler as ExcelHandler

def SQLTEST():

    result = "";

    DBConnect = SQLConnect.DBConnect()
    DBConnect.ConnectDB()
    sql_cmd = "select * from DownLoadList where DLName like N'"+"%T%" + "'"
    DLflag = DBConnect.GetDataTable(sql_cmd)
    ExcelHandler.setExcel(DLflag,r"D:\trtdr.xlsx")
   
    DBConnect.close()
    #sql = """\
    #        select top 15 * from FdfQALog
    #        """

    #table=DBConnect.Execute(sql)
    #for rows in table:
    #    if ( str(type(table[rows])) =="<class 'list'>"):
    #        print("SelectTable "+ rows)
    #        for row in table[rows]:
    #            print(row)
    #    elif ( str(type(table[rows])) =="<class 'str'>"):
    #        print(rows + " " + table[rows])

   

    #inputjson ={}
    #inputjson["ModType"]="Instest"
    #inputjson["Uno"]=0
    #inputjson["Vno"]=0
    #inputjson["Parent"]=0
    #inputjson["Type"]="Q"
    #inputjson["EmailFrom"]=""
    #inputjson["EmailTo"]=""
    #inputjson["EmailCC"]=""
    #inputjson["Subject"]=""
    #inputjson["Body"]=""
    #inputjson["Sno"]=0

    #outputjson ={}
    #outputjson["ErrMsg"]=""
    #outputjson["ResultSno"]=""

    #table=DBConnect.ExecuteSP("PR_FdfQALogMod",inputjson,outputjson)

    #for rows in table:
    #    if ( str(type(table[rows])) =="<class 'list'>"):
    #        print("SelectTable "+ rows)
    #        for row in table[rows]:
    #            print(row)
    #    elif ( str(type(table[rows])) =="<class 'str'>"):
    #        print(rows + " " + table[rows])
       
       
    #inputjson ={}
    #inputjson["Type"]="8"
    #inputjson["Vno"]=0
    #inputjson["Sno"]=0
    #inputjson["Uno"]=0
    #inputjson["Email"]=""
   

    #outputjson ={}


    #table=DBConnect.ExecuteSP("PR_FdfQALogSel",inputjson,outputjson)

    #for rows in table:
    #    if ( str(type(table[rows])) =="<class 'list'>"):
    #        print("SelectTable "+ rows)
    #        for row in table[rows]:
    #            print(row)
    #    elif ( str(type(table[rows])) =="<class 'str'>"):
    #        print(rows + " " + table[rows])
       



    return result

if __name__ == '__main__':
    try:
        print(SQLTEST());

    except Exception as ex:
       print(ex)

