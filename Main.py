# -*- coding:utf-8 -*-
import math
import random

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
    # print(docid_cont_list)
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

    # author
    print('[{}] {} -> Extracting the author of keywords ...'.format(TIME(), KEYSTR))
    author_key_dict = Keywords.extractInterestingKeywords(dataset, ARRAYID['author_type'])
    # print('> Keyword Author : {}'.format(" ".join(author_key_dict.keys())))
    author_list = list(author_key_dict.keys())
    # print(type(author_list), author_list)
    author_day_list, time_author_list, time_authorid_list = Keywords.timeDataAnalysis(dataset, author_list, ARRAYID['author_type'], KEY_TIME_INTERVAL)
    Keywords.visTimeData(author_day_list, time_author_list, author_list, "Author Total", KEY_VIS_AUTHOR_PATH)

    # pulisher
    print('[{}] {} -> Extracting the publisher of keywords ...'.format(TIME(), KEYSTR))
    publisher_key_dict = Keywords.extractInterestingKeywords(dataset, ARRAYID['pubname'])
    publisher_list = list(publisher_key_dict.keys())
    publisher_day_list, time_publisher_list, time_publisherid_list = Keywords.timeDataAnalysis(dataset, publisher_list, ARRAYID['pubname'], KEY_TIME_INTERVAL)
    Keywords.visTimeData(publisher_day_list, time_publisher_list, publisher_list, "Publisher Total", KEY_VIS_PUBLISHER_PATH)

    # 3. Emotion
    if os.path.exists(EMO_FILENAME):
        Emotion.statisticalEmotions(dataset, EMO_FILENAME)
        emotion_dict = Preprocessing.readPklFile(EMO_FILENAME)
    else:
        print('[{}] {} -> Not recommended! It takes too long ...'.format(TIME(), EMOSTR))

    # Manual Emotion
    manual_emo_list = [MANUAL_POSNUM, MANUAL_NEGNUM, MANUAL_EQUNUM]
    manual_emo_day_list, manual_time_emo_list, manual_emoid_list = Emotion.timeEmotionCountAnalysis(dataset, manual_emo_list, KEY_TIME_INTERVAL)
    Keywords.visTimeData(manual_emo_day_list, manual_time_emo_list, manual_emo_list, "Manual Emotion Total", EMO_VIS_MANUAL_PATH)

    # 4. Customized Keywords
    print('[{}] {} -> Extracting custom keywords ...'.format(TIME(), CUSSTR))
    gain_keywords = ["中國", "口罩", "經濟"]
    onekey_daylist = []
    onekey_timelist = None
    # one keyword numbers
    for key_i, onekey in enumerate(gain_keywords):
        print('[{}] {} -> {}  Processing ...'.format(TIME(), CUSSTR, onekey))
        folderpath = Customized.preEnv(key_i, onekey)

        # author
        custom_dataset, map_correlate = Customized.customRelated(dataset, map_dataset, map_nkey, onekey)
        map_correlate.pop(onekey)
        cusone_author_day_list, cusone_time_author_list, cusone_time_authorid_list = Keywords.timeDataAnalysis(custom_dataset, author_list, ARRAYID['author_type'], KEY_TIME_INTERVAL)
        Keywords.visTimeData(cusone_author_day_list, cusone_time_author_list, author_list, "Author:"+onekey, folderpath + os.sep + KEY_AUTHORJPG)

        # publisher
        cusone_publisher_day_list, cusone_time_publisher_list, cusone_time_publisherid_list = Keywords.timeDataAnalysis(custom_dataset, publisher_list, ARRAYID['pubname'], KEY_TIME_INTERVAL)
        Keywords.visTimeData(cusone_publisher_day_list, cusone_time_publisher_list, publisher_list, "Publisher:"+onekey, folderpath + os.sep + KEY_PUBLISHERJPG)
        # print(len(cusone_publisher_day_list), len(cusone_time_publisher_list))

        day_list = cusone_author_day_list
        # Initial onekey_timelist
        if onekey_timelist == None:
            onekey_daylist = day_list
            onekey_timelist = []
            onekey_timelist.append(gain_keywords)
            for d_i in range(0, len(day_list)):
                temp = []
                for k_i in range(0, len(gain_keywords)):
                    temp.append(0)
                onekey_timelist.append(temp)

        # Emotion: Sampling
        emo_day_num = EMO_SAMPLE_NUMS // len(day_list)
        # print(EMO_SAMPLE_NUMS, len(day_list), EMO_SAMPLE_NUMS // len(day_list))

        daysamid_dataset = []
        allsample_dataset = []
        for authorid_i in cusone_time_authorid_list[1:]:
            sumoneday = 0
            for auidone_j in authorid_i:  # array
                sumoneday += len(auidone_j)
            samples_dataset = []
            if sumoneday > 0:  # Skip empty arrayss
                for auidone_j in authorid_i:  # array
                    # print(auidone_j)
                    sample_nums = math.ceil((len(auidone_j) / sumoneday) * emo_day_num)
                    sample_nums = min(len(auidone_j), sample_nums)
                    samples = random.sample(auidone_j, sample_nums)  # No duplicate sampling
                    for sam_k in samples:
                        samples_dataset.append(map_dataset[sam_k][ARRAYID['docid']])
                        allsample_dataset.append(map_dataset[sam_k])
            daysamid_dataset.append(samples_dataset)

        # print(len(day_list), len(daysamid_dataset))
        # Analysis emotion
        Emotion.statisticalEmotions(allsample_dataset, folderpath + os.sep + EMO_SAMPLE_FILENAME)
        one_emotion_dict = Preprocessing.readPklFile(folderpath + os.sep + EMO_SAMPLE_FILENAME)

        emo_curves_num = ["pos", "neg", "neu"]
        emo_timelist = [emo_curves_num, ]
        for daysamarr_i in daysamid_dataset:
            emo_timedict = {"pos": 0, "neg": 0, "neu": 0}
            for sam_j in daysamarr_i:
                emo_val = one_emotion_dict[sam_j]
                if emo_val["pos"] > emo_val["neg"]:
                    emo_timedict["pos"] += 1
                elif emo_val["pos"] < emo_val["neg"]:
                    emo_timedict["neg"] += 1
                elif emo_val["pos"] == emo_val["neg"]:
                    emo_timedict["neu"] += 1
            emo_timelist.append([emo_timedict["pos"], emo_timedict["neg"], emo_timedict["neu"]])
        Keywords.visTimeData(day_list, emo_timelist, emo_curves_num, "Emotion:"+onekey, folderpath + os.sep + EMO_ONEKEYJPG)

        # Manual Emotion
        manual_emo_list = [MANUAL_POSNUM, MANUAL_NEGNUM, MANUAL_EQUNUM]
        manual_emo_day_list, manual_time_emo_list, manual_emoid_list = Emotion.timeEmotionCountAnalysis(custom_dataset, manual_emo_list, KEY_TIME_INTERVAL)
        Keywords.visTimeData(manual_emo_day_list, manual_time_emo_list, manual_emo_list, "Manual Emotion:" + onekey, folderpath + os.sep + EMO_MANUAL_JPG)

        # Correlated Keywords
        correlate_list, correlateid_set = Customized.customDayKeyword(map_nkey, cusone_author_day_list, cusone_time_authorid_list)

        # Prepare data
        headers = ["year", "month", "day"]\
                  + cusone_time_author_list[0] + ["author_total"]\
                  + cusone_time_publisher_list[0] + ["publisher_total"]\
                  + ["keywords_total"]\
                  + ["pos_count", "neg_count", "neu_count", "emo_score"]\
                  + manual_emo_list + ["manualemo_score"]
        for corkey_i in range(0, CUS_CORRELATED_KEYNUMS):
            headers += ["correlation_keyword"+str(corkey_i), "correlation_value"+str(corkey_i)]
        values = []
        for day_i, oneday in enumerate(day_list):
            temp = []
            temp.append(int(oneday[0:4]))
            temp.append(int(oneday[4:6]))
            temp.append(int(oneday[6:8]))

            temp += cusone_time_author_list[day_i+1]
            temp += [sum(cusone_time_author_list[day_i+1])]

            temp += cusone_time_publisher_list[day_i+1]
            temp += [sum(cusone_time_publisher_list[day_i+1])]

            # print(correlate_list[day_i])
            correlate_oneday_dict = correlate_list[day_i]
            # print(type(correlate_oneday_dict), correlate_oneday_dict)
            if onekey in correlate_oneday_dict:
                try:
                    onekey_timelist[day_i+1][key_i] = correlate_oneday_dict.pop(onekey)
                except:
                    pass
            temp += [len(correlate_oneday_dict)]

            # Emotion
            pos_count = emo_timelist[day_i + 1][0]
            neg_count = emo_timelist[day_i + 1][1]
            posaneg_count = pos_count+neg_count
            neu_count = emo_timelist[day_i + 1][2]
            score = 0
            if posaneg_count > 0:
                score = pos_count/posaneg_count - neg_count/posaneg_count
            temp += [pos_count, neg_count, neu_count, score]

            # Manual Emotion
            manual_pos = manual_time_emo_list[day_i+1][0]
            manual_neg = manual_time_emo_list[day_i+1][1]
            manual_equ = manual_time_emo_list[day_i+1][2]
            man_posaneg = manual_pos + manual_neg
            manual_emoscore = 0
            if man_posaneg > 0:
                manual_emoscore = manual_pos/man_posaneg - manual_neg/man_posaneg
            temp += [manual_pos, manual_neg, manual_equ, manual_emoscore]

            # Correlate Keywords
            for corkey_i in range(0, CUS_CORRELATED_KEYNUMS):
                if len(correlate_oneday_dict) > 0:
                    max_key = max(correlate_oneday_dict, key=correlate_oneday_dict.get)
                    max_value = correlate_oneday_dict[max_key]
                    correlate_oneday_dict.pop(max_key)
                else:
                    max_key = ""
                    max_value = 0
                temp += [max_key, max_value]

            values.append(temp)

        # print(headers, len(headers), len(values))
        # Save data to .csv file.
        Customized.dataSaveTocsv(headers, values, folderpath + os.sep + onekey + CUS_CSVFILENAME)

        docid_cont_list = Preprocessing.getIDCont(map_dataset, correlateid_set, ARRAYID['content'])  # Get content from the docid list.
        # Not recommended! It takes too long ...
        # Preprocessing.saveToTxt(docid_cont_list, folderpath + os.sep + CUS_CONTFILENAME)

    # One Key numbers list
    Keywords.visTimeData(onekey_daylist, onekey_timelist, gain_keywords, "Keywords Total", CUS_VIS_ONEKEY_PATH)

    # # Emotion
    # print('[{}] {} -> Statistical emotions ...'.format(TIME(), EMOSTR))
    # Emotion.statisticalEmotions(dataset, EMO_FILENAME)
    # map_emotion = Preprocessing.readPklFile(EMO_FILENAME)
    # if len(dataset) != len(map_emotion):
    #     raise Exception("Error -> Errors in data processing, inconsistent lengths！")
    # print('[{}] {} -> Logistic regression ...'.format(TIME(), EMOSTR))

    print(" ----------- End of data analysis ----------- ")


if __name__ == '__main__':
    mainAnalysis()