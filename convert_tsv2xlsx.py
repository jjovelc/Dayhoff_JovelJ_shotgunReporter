import sys
import csv

from xlsxwriter.workbook import Workbook
  
# Input file path
tsv_file = sys.argv[1]
# Output file path
xlsx_file = sys.argv[2]
  
# Add workshee to XlsxWriter workbook object
workbook = Workbook(xlsx_file)
worksheet = workbook.add_worksheet()
  
# Reading the tsv file.
read_tsv = csv.reader(open(tsv_file, 'r', encoding='utf-8'), delimiter='\t')
  
# move data from tsv to xlsx
for row, data in enumerate(read_tsv):
    worksheet.write_row(row, 0, data)
  
# Close xlsx file
workbook.close()
