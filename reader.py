#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28
@author: hudson

readData is the updated reader function.
It takes in a filename, (I.E. file.csv) checks the filetime is supported,
finds the file in the current directory, extracts the data and returns it
as a Pandas DataFrame.

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