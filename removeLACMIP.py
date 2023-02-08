# if you run the renaming script without first editing, then your images are for LACIP
import os

file_dir = r'F:\Herbarium imaging\PRU\QuickGuide\JPEG\successes\2023-02_successes\doubles'

files = os.listdir(file_dir)

for file in files:
  newfile = file.replace('LACMIP_', '').replace('_a', '')
  if newfile != file:
    try:
      os.rename(os.path.join(file_dir, file), os.path.join(file_dir, newfile))
    except:
      continue