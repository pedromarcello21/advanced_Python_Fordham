# Read all .xlsx files in the 'data' directory and output data to a text file
import os
import pandas as pd

def getFileList(ext, dir='.'):
   filenames = os.listdir(dir)
   filenameList = []
   for filename in filenames:
      if filename.endswith(ext):
         filenameList.append(filename)
   return filenameList

filenames = getFileList('.xlsx', dir='data')
if len(filenames) > 0:
   os.chdir('data') # change the working directory to data 'data' sub-folder
   dfall = pd.read_excel(filenames[0])
   for i in range(1, len(filenames)):
      df = pd.read_excel(filenames[i])
      dfall = dfall.append(df , ignore_index=True, sort=False)
      
   dfall.to_csv('all.txt')