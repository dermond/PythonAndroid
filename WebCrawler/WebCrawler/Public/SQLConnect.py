#資料庫套件
import pyodbc
import Public.SettingReader as SettingReader
class DBConnect():
    def __init__(self, secName=None,publicSetting=False):
        if secName is None:
            secName="connect"
        if publicSetting:
            self.server = SettingReader.getPublicSetting(secName,"server")
            self.database = SettingReader.getPublicSetting(secName,"database")
            self.username = SettingReader.getPublicSetting(secName,"username")
            self.password = SettingReader.getPublicSetting(secName,"password") 
            self.driver=SettingReader.getPublicSetting(secName,"driver")
            self.dbcon=None
        else:
            self.server = SettingReader.getSetting(secName,"server")
            self.database = SettingReader.getSetting(secName,"database")
            self.username = SettingReader.getSetting(secName,"username")
            self.password = SettingReader.getSetting(secName,"password") 
            self.driver=SettingReader.getSetting(secName,"driver")
            self.dbcon=None

    def ConnectDB(self,DBName=None):
        if DBName is not None:
            self.database=DBName
        cnxn = pyodbc.connect('DRIVER={'+self.driver+'};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password,autocommit=True)
        cnxn.cursor()
        self.dbcon=cnxn
        
    def Execute(self,sql, parameters = None):
        try:
            if parameters == None:
                return self.dbcon.execute(sql)
            else:
                return self.dbcon.execute(sql, parameters)
        except Exception as ex:
            raise ex

    def GetDataTable(self,sql, parameters = None):
        cursor = self.Execute(sql, parameters)
        try:
            rows=cursor.fetchall()
        except :
            return []
        return rows

    def StartTransaction(self):
        self.dbcon.autocommit=False

    def commit(self):
        self.dbcon.commit()

    def rollback(self):
        self.dbcon.rollback()

    def close(self):
        self.dbcon.close()
    