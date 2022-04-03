# -*- coding:utf-8 -*-
import csv

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

# According docid to extract Correlated Keywords
def customDayKeyword(map_nkey: 'dict[docid:[n_keywords]]', day_list, id_list):
    # print(len(day_list), len(id_list))
    id_list = id_list[1:]
    correlate_list: 'list[dict[keyword:nums]]' = []
    correlateid_set = set()
    for day_i in range(0, len(day_list)):
        id_set: 'docid' = set()
        correlate_dict = {}
        for source_j in id_list[day_i]:
            id_set = id_set | set(source_j)
            correlateid_set = correlateid_set | set(source_j)
        for docid_j in id_set:
            for key_k in map_nkey[docid_j]:
                if key_k not in correlate_dict:
                    correlate_dict[key_k] = 1
                else:
                    correlate_dict[key_k] += 1
        correlate_list.append(correlate_dict)
    return correlate_list, correlateid_set

def dataSaveTocsv(headers, values, filepath):
    with open(filepath, "w", newline='', encoding='utf-8_sig') as fp:
        writer = csv.writer(fp)
        writer.writerow(headers)
        writer.writerows(values)
