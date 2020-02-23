#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 09:20:28 2020
@author: hudson

This code takes in 3 command-line arguements (nodeDataFile, edgeDataFile, fileType)
where nodeDataFile and edgeDataFile are file names
and fileType specifies the type for nodeDataFile and edgeDataFile

readData first checks that the filetype is supported before looking in the
current working directory for files with names nodeDataFile and edgeDataFile.

If it finds them, it returns them as Pandas DataFrames.

"""

#Import system specific parameters and functions
import sys
# Import libraries
import pandas as pd


# List of supported file types
sptdTypes = ['csv']
    
## MAIN ##
def readData(file):
    fileType = getFileType(file)
    isTypeSptd(fileType)
    rawData = retrieve_csv(file)
    return rawData
    

def getFileType(file):
    fileType = ""
    try:
        indx = file.index(".")
    except ValueError:
        # TODO: Infer type from filename
        print("ERROR: file not found.")
        sys.exit(1)
        
    i = indx + 1
    while (i < len(file)):
        fileType = fileType + file[i]
        i += 1
    return fileType

# Checks if filetype is supported
def isTypeSptd(fileType):
    isTypeSptd = 0
    for file in sptdTypes:
        if fileType == file:
            isTypeSptd = 1
            
    if (isTypeSptd == 0):
        print(f"ERROR: file type '{fileType}' is not a supported type.")
        sys.exit(1)
    else:
        return

# Attempts to retrieve data from working directory
def retrieve_csv(file):
    try: 
        data = pd.read_csv(file)
    except FileNotFoundError:
        print(f"ERROR: file '{file}' does not exist in working directory.")
        sys.exit(1)
    return data


data = readData("Tester.csv")
print(data)