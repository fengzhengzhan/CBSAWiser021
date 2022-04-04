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
        before_datetime = None
        for sh in xlsx.sheets():  # Traversing data to save to an array
            for r in range(sh.nrows):
                temp_data = sh.row_values(r)
                try:
                    # Convert time to datetime format
                    temp_data[ARRAYID['pubdate']] = xlrd.xldate.xldate_as_datetime(temp_data[ARRAYID['pubdate']], 0)
                    before_datetime = temp_data[ARRAYID['pubdate']]
                except Exception as e:
                    # origin:pass todo test
                    temp_data[ARRAYID['pubdate']] = before_datetime
                temp_array.append(temp_data)

        with open(save_filename, 'wb') as file:  # Save data as pkl Increase speed on further processing
            pickle.dump(temp_array, file)

# Read pkl rile
def readPklFile(filename):
    with open(filename, 'rb') as file:
        temp = pickle.load(file)
    return temp

# Get docid map contents
def getIdMap(dataset):
    datasetmap = {}
    for one in dataset:
        datasetmap[one[ARRAYID['docid']]] = one
    return datasetmap


def getIDCont(map_dataset, pre_id_cont, coolid):
    temp_list = []
    for each in pre_id_cont:
        temp_list.append(map_dataset[each][coolid])
    return temp_list

# Data display preservation
def saveToTxt(textlist, filename):
    text = ""
    for text_i in textlist:
        text += str(text_i) + "\n\n"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)


