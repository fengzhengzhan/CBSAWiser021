# -*- coding:utf-8 -*-
import xlrd
import pickle

from Config import *

# Environment preparation, file creation
def readyEnv():
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    if not os.path.exists(ANALYSIS_PATH):
        os.mkdir(ANALYSIS_PATH)
    if not os.path.isfile(DATA_FILENAME):
        raise Exception("Error -> There is no data file, please copy the data file to the data directory.")


# Save data as pkl Increase speed on further processing
def excelToPickle(filename=DATA_FILENAME, save_filename=DATA_SAVE_FILENAME):
    if not os.path.exists(save_filename):  # Data conversion will not be performed if the pkl file exists
        print('[{}] This is the first read, file conversion in progress (3min) ...'.format(TIME()))
        xlsx = xlrd.open_workbook(filename)  # Open the workbook, the first time of reading the file takes ard 2 mins
        temp_array = []
        for sh in xlsx.sheets():  # Traversing data to save to an array
            for r in range(sh.nrows):
                temp_data = sh.row_values(r)
                try:
                    # Convert time to datetime format
                    temp_data[ARRAYID['pubdate']] = xlrd.xldate.xldate_as_datetime(temp_data[ARRAYID['pubdate']], 0)
                except Exception as e:
                    pass
                temp_array.append(temp_data)

        with open(save_filename, 'wb') as file:  # Save data as pkl Increase speed on further processing
            pickle.dump(temp_array, file)

# Read pkl rile
def readPklFile(filename):
    with open(filename, 'rb') as file:
        temp = pickle.load(file)
    return temp