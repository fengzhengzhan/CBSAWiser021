# -*- coding:utf-8 -*-
import datetime
import pickle
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import threading
from cnsenti import Sentiment
from snownlp import SnowNLP

from Config import *

# Statistical emotions

def emotionAnalysis(one_data, senti):
    temp_dict = {}
    try:
        result = senti.sentiment_count(one_data[ARRAYID['content']])
        temp_dict[one_data[ARRAYID['docid']]] = result
    except Exception as e:
        result = {'words': 0, 'sentences': 0, 'pos': 0, 'neg': 0}
        temp_dict[one_data[ARRAYID['docid']]] = result
    # try:
    #     s = SnowNLP(one_data[ARRAYID['content']])
    #     score = s.sentiments
    #     temp_dict[one_data[ARRAYID['docid']]] = score
    # except Exception as e:
    #     score = 0
    #     temp_dict[one_data[ARRAYID['docid']]] = score
    return temp_dict

# class KeyThread(threading.Thread):
#     def __init__(self, func, args):
#         super(KeyThread, self).__init__()
#         self.func = func
#         self.args = args
#
#     def run(self):
#         self.result = self.func(*self.args)
#
#     def get_result(self):
#         try:
#             return self.result
#         except Exception as e:
#             return None

def thread_analysis(split_dataset, senti, map_emotion):
    # thread_list = []
    # for each in split_dataset:
    #     t = KeyThread(emotionAnalysis, args=(each, senti,))
    #     t.setDaemon(True)
    #     t.start()
    #     thread_list.append(t)
    # for one in thread_list:
    #     one.join()
    #     result = one.get_result()
    #     for k, v in result.items():
    #         map_emotion[k] = v

    threadPool = ThreadPoolExecutor(max_workers=THREAD_NUM)
    thread_list = []
    for each in split_dataset:
        future = threadPool.submit(emotionAnalysis, each, senti)
        result = future.result()
        for k, v in result.items():
            map_emotion[k] = v
    threadPool.shutdown(wait=True)


def statisticalEmotions(dataset, analysis_emotion_filename, ret_res=False):
    if not os.path.exists(analysis_emotion_filename) or ret_res:
        if MULTI_MODE:
            print('[{}] This is the first time for emotion analysis in multiprocessing mode ...'.format(TIME()))
            cpu_cnt = multiprocessing.cpu_count()
            each_datalen = int(len(dataset) / cpu_cnt)
            # print(len(dataset), each_datalen, cpu_cnt)

            map_emotion = multiprocessing.Manager().dict()
            senti = Sentiment()
            # process_list = []
            # for i in range(cpu_cnt):
            #     print("{} / {}".format(each_datalen * i, each_datalen * (i + 1)))
            #     if i == cpu_cnt - 1:
            #         p = multiprocessing.Process(target=thread_analysis,
            #                                     args=(dataset[each_datalen * i:], senti, map_emotion,))  # Instantiating process objects
            #     else:
            #         p = multiprocessing.Process(target=thread_analysis,
            #                                     args=(dataset[each_datalen * i:each_datalen * (i + 1)], senti, map_emotion,))  # Instantiating process objects
            #     p.daemon = True
            #     p.start()
            #     process_list.append(p)
            # for one in process_list:
            #     one.join()

            pool = multiprocessing.Pool(processes=cpu_cnt)
            for i in range(cpu_cnt):
                print("{} / {}".format(each_datalen * i, each_datalen * (i + 1)))
                if i == cpu_cnt - 1:
                    pool.apply_async(thread_analysis, (dataset[each_datalen * i:], senti, map_emotion,))  # Instantiating process objects
                else:
                    pool.apply_async(thread_analysis, (dataset[each_datalen * i:each_datalen * (i + 1)], senti, map_emotion,))  # Instantiating process objects
            pool.close()
            pool.join()

            map_emotion = dict(map_emotion)
        else:
            print('[{}] This is the first time for emotion analysis(#->1000) ...'.format(TIME()))
            map_emotion = {}
            senti = Sentiment()
            for i, one in enumerate(dataset):
                try:
                    result = senti.sentiment_count(one[ARRAYID['content']])
                    map_emotion[one[ARRAYID['docid']]] = result
                    # print(result)
                    if i % 40000 == 0:
                        print("\n{} / {}  ".format(i, len(dataset)), end="")
                    if i % 1000 == 0:
                        print("#", end="")
                except Exception as e:
                    result = {'words': 0, 'sentences': 0, 'pos': 0, 'neg': 0}
                    map_emotion[one[ARRAYID['docid']]] = result
        print()
        print('[{}] The length after analysis is {}. ...'.format(TIME(), len(map_emotion)))
        if ret_res:
            return map_emotion
        else:
            with open(analysis_emotion_filename, 'wb') as file:  # Save analysis results.
                pickle.dump(map_emotion, file)


# Plotting the percentage of speech in each camp according to the timeline
def timeEmotionCountAnalysis(dataset, data_list, day_interval):
    first_date = None
    second_date = None
    dt = datetime.timedelta(days=day_interval)
    day_list = []
    manual_emo_list = [data_list, ]
    data_id_list = [data_list, ]

    # Init the dict of data numbers.
    emo_num_dict = {}
    data_id_dict = {}
    for each in data_list:
        emo_num_dict[each] = 0
        data_id_dict[each] = []
    # data loop
    i = -1
    while i < len(dataset)+1:  # Leave one left
        i += 1
        # Time analysis
        if i < len(dataset):
            now_date = dataset[i][ARRAYID['pubdate']]
        # Determine if it is a time type
        if isinstance(now_date, datetime.datetime):
            #print(i,now_date)
            if first_date is None:  # First time assignment
                temp_date = str(now_date.year) + "-" + str(now_date.month) + "-" + str(now_date.day)
                first_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")
                second_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d") + dt
                # print(first_date, second_date)
            # Determine time range
            if i < len(dataset) and first_date <= now_date <= second_date:
                positiveemo_count = dataset[i][ARRAYID['positiveemo_count']]
                negativeemo_count = dataset[i][ARRAYID['negativeemo_count']]
                # Result counts
                if positiveemo_count > negativeemo_count:
                    emo_num_dict[MANUAL_POSNUM] += 1
                    data_id_dict[MANUAL_POSNUM].append(dataset[i][ARRAYID['docid']])
                elif positiveemo_count < negativeemo_count:
                    emo_num_dict[MANUAL_NEGNUM] += 1
                    data_id_dict[MANUAL_NEGNUM].append(dataset[i][ARRAYID['docid']])
                elif positiveemo_count == negativeemo_count and positiveemo_count != 0:
                    emo_num_dict[MANUAL_EQUNUM] += 1
                    data_id_dict[MANUAL_EQUNUM].append(dataset[i][ARRAYID['docid']])
            else:
                temp_num = []
                temp_id = []
                for one in data_list:
                    temp_num.append(emo_num_dict[one])  # Guarantee order
                    temp_id.append(data_id_dict[one])
                manual_emo_list.append(temp_num)
                data_id_list.append(temp_id)
                day_list.append(str(second_date)[0:4] + str(second_date)[5:7] + str(second_date)[8:10])
                # Init the dict of data numbers.
                emo_num_dict = {}
                data_id_dict = {}
                for each in data_list:
                    emo_num_dict[each] = 0
                    data_id_dict[each] = []
                first_date = second_date
                second_date = second_date + dt
                #print(second_date, "--------", dt)
                if i < len(dataset) and first_date <= now_date <= second_date:
                    i -= 1

    return day_list, manual_emo_list, data_id_list

# Data display preservation
def saveToTxt(text, filename):
    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(text)
        f.write("\n")

# Keyword extraction, and save
def extrectAnalysisKeyWords(emode, exdict, numn, remove_words, weight_enable):
    text = ""
    activen = 0
    while True:
        if activen >= numn:
            break
        max_key = max(exdict, key=exdict.get)
        max_value = exdict[max(exdict, key=exdict.get)]
        if max_key not in remove_words:
            activen += 1
            if weight_enable:
                text += " " + str(max_key) + ":" + str(max_value)
            else:
                text += " " + str(max_key)
            if emode == TIME_MODE and activen == 1:
                global INTERESTING_TEXT
                INTERESTING_TEXT += str(max_key) + " "
        exdict.pop(max_key)
    text += "\n"
    return text


# Traversing data for conditional analysis
# conditionAnalysis(dataset, nkey_array, [TIME_ANALYSIS, EMOTION_ANALYSIS])
def conditionAnalysis(dataset, nkey_array, mode):
    if mode:
        # Time analysis
        first_date, second_date = None, None
        dt = datetime.timedelta(days=TIME_INTERVAL)
        time_dict = {}
        # Emotion analysis
        emo_num_dict = {ZEROEQUNUM:0, MANUAL_EQUNUM:0, MANUAL_POSNUM:0, MANUAL_NEGNUM:0}
        emo_dict = {ZEROEQU: {}, EQU:{}, POS:{}, NEG:{}}

        # data loop
        for i in range(0, len(dataset)):
            # Time analysis
            if TIME_ANALYSIS in mode:
                now_date = dataset[i][ARRAYID['pubdate']]
                # Determine if it is a time type
                if isinstance(now_date, datetime.datetime):
                    if first_date is None:  # First time assignment
                        temp_date = str(now_date.year)+"-"+str(now_date.month)+"-"+str(now_date.day)
                        first_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")
                        second_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")+dt
                        # print(first_date, second_date)
                    # Determine time range
                    if first_date <= now_date <= second_date and i != len(dataset)-1:
                        for nk in range(0, EACH_LINE_KEYWORDS):
                            nkword = nkey_array[i][nk]
                            if nkword in time_dict:
                                time_dict[nkword] += 1
                            else:
                                time_dict[nkword] = 1
                            if nkword in INTERESTING_WORDS:
                                tt = str('keyword: '+str(nkword)+"\n"
                                         +now_date.strftime("%Y-%m-%d-%H:%M:%S")+"\n"
                                         +'positiveemo_count: '+str(dataset[i][ARRAYID['positiveemo_count']])+"\n"
                                         +'negativeemo_count: '+str(dataset[i][ARRAYID['negativeemo_count']])+"\n"
                                         +str(dataset[i][ARRAYID['content']].encode("gbk", 'ignore').decode("gbk", "ignore")).replace('\s+', '\\\\').replace('\n', '\\\\')+"\n")
                                saveToTxt(tt, INTERESTING_CONTENT_FILENAME)

                    else:
                        # Find weekly reviews
                        timetext = str(first_date.strftime("%Y-%m-%d-%H:%M:%S")) + "->" + str(second_date.strftime("%Y-%m-%d-%H:%M:%S"))
                        timetext += extrectAnalysisKeyWords(TIME_MODE, time_dict, EACH_WEEKEND_N, KEY_STOP_WORDS, ENABLE_TIME_WEIGHT)
                        saveToTxt(timetext, TIME_TXT_FILENAME)
                        time_dict = {}
                        first_date = second_date
                        second_date = second_date+dt

            # emotion trend analysis
            if EMOTION_ANALYSIS in mode:
                negativeemo_count = dataset[i][ARRAYID['negativeemo_count']]
                positiveemo_count = dataset[i][ARRAYID['positiveemo_count']]
                # Result counts
                if negativeemo_count > positiveemo_count:
                    emo_num_dict[MANUAL_NEGNUM] += 1
                elif negativeemo_count < positiveemo_count:
                    emo_num_dict[MANUAL_POSNUM] += 1
                elif negativeemo_count == positiveemo_count and positiveemo_count != 0:
                    emo_num_dict[MANUAL_EQUNUM] += 1
                elif negativeemo_count == positiveemo_count and positiveemo_count == 0:
                    emo_num_dict[ZEROEQUNUM] += 1

                # Keywords statistic
                for emonk in range(0, EMO_EACH_LINE):
                    emonkword = nkey_array[i][emonk]
                    if negativeemo_count > positiveemo_count:
                        if emonkword in emo_dict[NEG]:
                            emo_dict[NEG][emonkword] += 1
                        else:
                            emo_dict[NEG][emonkword] = 1
                    elif negativeemo_count < positiveemo_count:
                        if emonkword in emo_dict[POS]:
                            emo_dict[POS][emonkword] += 1
                        else:
                            emo_dict[POS][emonkword] = 1
                    elif negativeemo_count == positiveemo_count and positiveemo_count != 0:
                        if emonkword in emo_dict[EQU]:
                            emo_dict[EQU][emonkword] += 1
                        else:
                            emo_dict[EQU][emonkword] = 1
                    elif negativeemo_count == positiveemo_count and positiveemo_count == 0:
                        if emonkword in emo_dict[ZEROEQU]:
                            emo_dict[ZEROEQU][emonkword] += 1
                        else:
                            emo_dict[ZEROEQU][emonkword] = 1

                if i == len(dataset)-1:
                    emotext = str(emo_num_dict) + "\n\n"
                    for emok, emov in emo_dict.items():
                        emotext += str(emok) + " "
                        emotext += extrectAnalysisKeyWords(EMO_MODE, emov, EACH_EMO_N, KEY_STOP_WORDS, ENABLE_EMO_WEIGHT)
                        emotext += "\n"
                    saveToTxt(emotext, EMO_TXT_FILENAME)

            # Show progress of processing
            if i % 80000 == 0:
                print("\n{} / {}  ".format(i, len(dataset)), end="")
            if i % 1000 == 0:
                print("#", end="")