#list資料 存成excel
def setExcel(data,path):
    import pandas as pd
    import xlsxwriter

    request = False
    with xlsxwriter.Workbook(path) as workbook:
        worksheet = workbook.add_worksheet()
        for row_num, data in enumerate(data):
            worksheet.write_row(row_num, 0, data)
    request = True
    return request
