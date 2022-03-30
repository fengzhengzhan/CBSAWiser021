from Config import *

def preEnv(index, folderWord):
    try:
        folderpath = ANALYSIS_PATH + os.sep + file_time + "_" + folderWord
        os.mkdir(folderpath)
    except Exception as e:
        folderpath = ANALYSIS_PATH + os.sep + file_time + "_" + "index" + index
        os.mkdir(folderpath)
    return folderpath

def customRelated(map_dataset, map_nkey, onekey):
    custom_dataset = []
    map_correlate = {}
    for k, v in map_nkey.items():
        if onekey in v:
            custom_dataset.append(map_dataset[k])
            for eachv in v:
                if eachv not in map_correlate:
                    map_correlate[eachv] = 1
                else:
                    map_correlate[eachv] += 1

    return custom_dataset, map_correlate


def dataSaveTocsv():
    pass
