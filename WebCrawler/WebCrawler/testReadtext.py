import Service.SettingReader as SettingReader


if __name__ == '__main__':

    secName="connect"
    server = SettingReader.getSetting(secName,"server")
    print(server)

    SettingReader.setSetting(secName,"test",9999)

    server = SettingReader.getSetting(secName,"test")
    print(server)

    SettingReader.setSetting(secName,"test",8787)

    server = SettingReader.getSetting(secName,"test")
    print(server)

