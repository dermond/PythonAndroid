#資料庫套件
import pyodbc
import Service.SettingReader as SettingReader


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

    def ConnectDB(self, DBName=None, max_retries=5, retry_interval=5, timeout=10):
       if DBName is not None:
           self.database = DBName
    
       connection_string = f'DRIVER={{{self.driver}}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
    
       for attempt in range(max_retries):
           try:
                cnxn = pyodbc.connect(connection_string, autocommit=True, timeout=timeout)
                self.dbcon = cnxn
                return
           except pyodbc.Error as e:
                print(f"連接失敗，重試 {attempt + 1}/{max_retries}...")
                time.sleep(retry_interval)
    
       raise Exception("無法連接到數據庫")
        
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
    