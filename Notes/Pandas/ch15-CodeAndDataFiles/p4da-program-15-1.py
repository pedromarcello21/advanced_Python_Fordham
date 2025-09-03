# display the list of .xlsx files in a given directory
import os

def getFileList(ext, dir='.'):
   filenames = os.listdir(dir)
   filenameList = []
   for filename in filenames:
      if filename.endswith(ext):
         filenameList.append(filename)
   return filenameList

filenames = getFileList('.xlsx', dir='data')
print(filenames)
