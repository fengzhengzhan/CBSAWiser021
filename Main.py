# -*- coding:utf-8 -*-
from Config import *
import Emotion
import Keywords
import Preprocessing


def mainAnalysis():
    print(" ----------- Start of data analysis ----------- ")

    # 1. Preprocessing
    Preprocessing.readyEnv()
    Preprocessing.excelToPickle()
    print('[{}] {} -> File reading in progress (6s) ...'.format(TIME(), PRESTR))
    dataset: list[list] = Preprocessing.readPklFile(DATA_SAVE_FILENAME)  # This function reads data in excel and returns the file data in 6s
    datasetmap = Preprocessing.getIdMap(dataset)
    docid_content = Preprocessing.getIDCont(datasetmap, PRE_ID_CONT)
    # print(docid_content)
    print('[{}] {} -> Keyword extraction of data ...'.format(TIME(), PRESTR))
    # print(dataset[1], type(dataset))

    # 2. Keywords
    Keywords.extractAllKeywords(dataset, KEY_NKEY_FILENAME)
    print('[{}] {} -> Read keyword information ...'.format(TIME(), KEYSTR))
    allkey_dict = Preprocessing.readPklFile(KEY_NKEY_FILENAME)  # Keyword file reading
    print('[{}] {} -> File reading completed. len_dataset:{} <-> len_nkey_dict:{}'.format(TIME(), KEYSTR, len(dataset), len(allkey_dict)))
    if len(dataset) != len(allkey_dict):
        raise Exception("Error -> Errors in data processing, inconsistent lengths！")
    nkey_dict, wordclouddict = Keywords.extractNKeywords(allkey_dict, KEY_NKEY)  # wordclouddict contains all keys and weights.
    # print(len(nkey_dict), wordclouddict)
    print('[{}] {} -> Word cloud analysis of data ...'.format(TIME(), KEYSTR))
    Keywords.visWordCloud(wordclouddict)
    print('[{}] {} -> Extracting the source of keywords ...'.format(TIME(), KEYSTR))
    source_key_dict = Keywords.extractSourceKeywords(dataset)
    # print(source_key_dict)
    print('> Keyword Source : {}'.format(" ".join(source_key_dict.keys())))
    source_list = list(source_key_dict.keys())
    # print(type(source_list), source_list)
    Keywords.visSourceTime(dataset, source_list)


    # # dataset sort according to time
    # # 1. Keyword analysis by time ()
    # print('[{}] Step 1: Time analysis of data ...'.format(TIME()))
    # print('[{}] Step 2: Emotion analysis of data ...'.format(TIME()))
    # print('[{}] Step 3: Keyword extraction and filtering ...'.format(TIME()))
    # conditionAnalysis(dataset, nkey_array, [TIME_ANALYSIS, EMOTION_ANALYSIS])
    #
    # print("\n", '[{}] Keyword Time Analysis ...'.format(TIME()))
    # print(INTERESTING_TEXT)

    print(" ----------- End of data analysis ----------- ")


if __name__ == '__main__':
    mainAnalysis()
