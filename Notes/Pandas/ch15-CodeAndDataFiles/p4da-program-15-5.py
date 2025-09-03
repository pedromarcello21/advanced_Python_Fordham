# find row labels and column headings in a worksheet
from openpyxl import load_workbook

# Read an .xlsx file, access a specific worksheet
divname = 'diva'
filename = 'incstmt-' + divname + '.xlsx'
workbook = load_workbook(filename, data_only=True)
worksheet = workbook['IncomeStatement']

rowcodes = ('SALE', 'CGS', 'SGA', 'ADV', 'DEP', 'RENT', 'OTHX')
colcodes = ('Act2019', 'Act2020', 'Proj2021')
rowdict = {}
coldict = {}
for row in worksheet.rows:
    for cell in row:
        #print(cell.row, cell.column, cell.coordinate, cell.value)
        if cell.value in rowcodes:
            rowdict[cell.value] = (cell.column, cell.row)
        elif cell.value in colcodes:
            coldict[cell.value] = (cell.column, cell.row)
print(rowdict)
print(coldict)
