# -*- coding:utf-8 -*-
from Config import *
import Emotion
import Keywords
import Preprocessing
import Customized


def mainAnalysis():
    print(" ----------- Start of data analysis ----------- ")

    # 1. Preprocessing
    Preprocessing.readyEnv()
    Preprocessing.excelToPickle()
    print('[{}] {} -> File reading in progress (6s) ...'.format(TIME(), PRESTR))
    dataset: list[list] = Preprocessing.readPklFile(DATA_SAVE_FILENAME)  # This function reads data in excel and returns the file data in 6s
    map_dataset = Preprocessing.getIdMap(dataset)
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
    map_nkey, wordclouddict = Keywords.extractNKeywords(allkey_dict, KEY_NKEY)  # wordclouddict contains all keys and weights.
    print("> Keywords : {}".format(wordclouddict))
    # print(len(map_nkey), wordclouddict)
    print('[{}] {} -> Word cloud analysis of data ...'.format(TIME(), KEYSTR))
    Keywords.visWordCloud(wordclouddict)
    print('[{}] {} -> Extracting the source of keywords ...'.format(TIME(), KEYSTR))
    source_key_dict = Keywords.extractSourceKeywords(dataset)
    # print(source_key_dict)
    # print('> Keyword Source : {}'.format(" ".join(source_key_dict.keys())))

    source_list = list(source_key_dict.keys())
    # print(type(source_list), source_list)
    day_list, time_source_list = Keywords.timeSourceAnalysis(dataset, source_list, KEY_SOURCETIME_INTERVAL)
    # for oneday in day_list:
    #     print(int(oneday[0:4]), int(oneday[4:6]), int(oneday[6:8]))
    Keywords.visTimeSource(day_list, time_source_list, source_list, "Total", KEY_VIS_SOURCE_PATH)

    # 3. Customized Keywords
    print('[{}] {} -> Extracting custom keywords ...'.format(TIME(), CUSSTR))
    gain_keywords = ["新冠", "檢測", "中國", "口罩", "經濟"]
    for idx, one in enumerate(gain_keywords):
        print('[{}] {} -> {}  Processing ...'.format(TIME(), CUSSTR, one))
        folderpath = Customized.preEnv(idx, one)
        custom_dataset, map_correlate = Customized.customRelated(map_dataset, map_nkey, one)
        cusone_day_list, cusone_time_source_list = Keywords.timeSourceAnalysis(custom_dataset, source_list, KEY_SOURCETIME_INTERVAL)
        Keywords.visTimeSource(cusone_day_list, cusone_time_source_list, source_list, one, folderpath + os.sep + KEY_SOURCEJPG)


    gain_id_content = ['2020021100002988743', '2020021100000087375']
    docid_content = Preprocessing.getIDCont(map_dataset, gain_id_content)  # Get content from the docid list.
    #
    #
    # # Emotion
    # print('[{}] {} -> Statistical emotions ...'.format(TIME(), EMOSTR))
    # Emotion.statisticalEmotions(dataset, EMO_FILENAME)
    # map_emotion = Preprocessing.readPklFile(EMO_FILENAME)
    # if len(dataset) != len(map_emotion):
    #     raise Exception("Error -> Errors in data processing, inconsistent lengths！")
    # print('[{}] {} -> Logistic regression ...'.format(TIME(), EMOSTR))



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