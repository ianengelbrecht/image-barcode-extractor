import csv
import os

file_dir = r'F:\Herbarium imaging\temp\2023\2023-02-07'

files = os.listdir(file_dir)

with open('newnames.csv') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    original = row['original']
    newname = row['new']
    for file in files:
      if original in file:
        newfile = file.replace(original, newname)

        #the list we have is the barcode in each image, and because different images might have the same barcodes...
        success = False
        count = 0
        while not success:
          try:
            os.rename(os.path.join(file_dir, file), os.path.join(file_dir, newfile)) 
            success = True
          except:
            filenameparts = '.'.split(newfile)
            filetype = '.' + filenameparts.pop()
            newfile = '.'.join(filenameparts)
            subscript = chr(ord('a') + count)
            if '_' in newfile:
              newfile = '_'.split(newfile)[0] + '_' + subscript
            else:
              newfile = newfile + '_' + subscript
            newfile = newfile + filetype
        continue
    
    