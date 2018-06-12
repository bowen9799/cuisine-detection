
import xlwt
import xlrd
from xlrd import open_workbook
from xlutils.copy import copy

class Sheet:
    def __init__(self,sheet_name,work_book):
        self.workbook = work_book
        self.sheet_name=sheet_name
        self.sheet_DATA=[]
        self.booksheet = self.workbook.add_sheet(self.sheet_name, cell_overwrite_ok=True)

    def add_sheet_data(self,sheet_data):
        self.sheet_DATA.append(sheet_data)

    def write_sheet(self):
        for i,row in enumerate(self.sheet_DATA):
            for j,col in enumerate(row):
                self.booksheet.write(i,j,col)


class XlsHelper:
    def __init__(self):
        self.workbook=xlwt.Workbook(encoding='utf-8')
        self.sheets={}

    def add_sheet(self,sheet_name):
        self.sheets[sheet_name] = Sheet(sheet_name,self.workbook)

    def add_sheet_data(self,sheet_name,sheet_data):
        spec_sheet = self.sheets.get(sheet_name)
        if spec_sheet != None:
            spec_sheet.add_sheet_data(sheet_data)
        else:
            print(" None sheet %s Found",sheet_name)

    def save(self,file_path):
        for item in self.sheets.items():
            item[1].write_sheet()
        self.workbook.save(file_path)


def write_sheet():
    HEAD = ('学号', '姓名', '年龄', '性别', '成绩')
    DATA1 = ('1001', 'A', '11', '男', '12')
    DATA2 = ('1002', 'B', '12', '女', '22')
    DATA3 = ('1003', 'C', '13', '女', '32')
    DATA4 = ('1004', 'D', '14', '男', '52')

    xls_writer = XlsHelper()
    xls_writer.add_sheet("Sheet One")
    xls_writer.add_sheet("Sheet Two")
    xls_writer.add_sheet_data("Sheet One", HEAD)
    xls_writer.add_sheet_data("Sheet One", DATA1)
    xls_writer.add_sheet_data("Sheet One", DATA2)
    xls_writer.add_sheet_data("Sheet One", DATA3)

    xls_writer.add_sheet_data("Sheet Two", HEAD)
    xls_writer.add_sheet_data("Sheet Two", DATA3)
    xls_writer.add_sheet_data("Sheet Two", DATA4)
    xls_writer.add_sheet_data("Sheet Two", DATA1)
    xls_writer.add_sheet_data("Sheet Two", DATA2)

    xls_writer.save("/mnt/hgfs/E/tmp/grade2.xls")


def read_excel(xls_file):
    workbook = xlrd.open_workbook(xls_file)
    sheet1_name= workbook.sheet_names()[0]
    sheet1 = workbook.sheet_by_name(sheet1_name)
    print (sheet1.name,sheet1.nrows,sheet1.ncols)
    cols = sheet1.col_values(0)
    for col in cols:
        if col == '':
            cols.remove(col)
    # print (cols)
    return cols


def append_excel_one_row(xls_file,values):
    rexcel = open_workbook(xls_file)
    rows = rexcel.sheets()[0].nrows
    excel = copy(rexcel)
    table = excel.get_sheet(0)
    # values =  ('1004', 'D', '14', '男', '52')
    row = rows
    index = 0
    for value in values:
        table.write(row, index, value)
        index +=1
    excel.save(xls_file)

#append_excel_one_row("./test3.xls", ('1004', 'D', '14', '男', '52'))
#append_excel_one_row("./test3.xls",())
#append_excel_one_row("./test3.xls", ('1004', 'D', '14', '男', '52'))
