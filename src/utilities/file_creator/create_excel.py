# create_excel.py

# .xlsx: excel files

from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = 'Sheet1'
ws.append(['Name', 'Age', 'City'])
ws.append(['Alice', 25, 'New York'])
wb.save('./test_files/example.xlsx')

print('Created example.xlsx')
