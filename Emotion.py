# -*- coding:utf-8 -*-
import datetime
import pickle
import multiprocessing
import threading
from cnsenti import Sentiment

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
    return temp_dict

class KeyThread(threading.Thread):
    def __init__(self, func, args):
        super(KeyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return None

def thread_analysis(split_dataset, senti, map_emotion):
    thread_list = []
    for each in split_dataset:
        t = KeyThread(emotionAnalysis, args=(each, senti,))
        t.setDaemon(True)
        t.start()
        thread_list.append(t)
    for one in thread_list:
        one.join()
        result = one.get_result()
        for k, v in result.items():
            map_emotion[k] = v


def statisticalEmotions(dataset, analysis_emotion_filename):
    if not os.path.exists(analysis_emotion_filename):
        if MULTI_MODE:
            print('[{}] This is the first time for emotion analysis in multiprocessing mode ...'.format(TIME()))
            cpu_cnt = multiprocessing.cpu_count()
            each_datalen = int(len(dataset) / cpu_cnt)
            # print(len(dataset), each_datalen, cpu_cnt)

            map_emotion = multiprocessing.Manager().dict()
            senti = Sentiment()
            process_list = []
            for i in range(cpu_cnt):
                print("{} / {}".format(each_datalen * i, each_datalen * (i + 1)))
                if i == cpu_cnt - 1:
                    p = multiprocessing.Process(target=thread_analysis,
                                                args=(dataset[each_datalen * i:], senti, map_emotion,))  # 实例化进程对象
                else:
                    p = multiprocessing.Process(target=thread_analysis,
                                                args=(dataset[each_datalen * i:each_datalen * (i + 1)], senti, map_emotion,))  # 实例化进程对象
                p.daemon = True
                p.start()
                process_list.append(p)
            for one in process_list:
                one.join()
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
        with open(analysis_emotion_filename, 'wb') as file:  # Save analysis results.
            pickle.dump(map_emotion, file)


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
def conditionAnalysis(dataset, nkey_array, mode):
    if mode:
        # Time analysis
        first_date, second_date = None, None
        dt = datetime.timedelta(days=TIME_INTERVAL)
        time_dict = {}
        # Emotion analysis
        emo_num_dict = {ZEROEQUNUM:0, EQUNUM:0, POSNUM:0, NEGNUM:0}
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
                                tt = str('keyward: '+str(nkword)+"\n"
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
                    emo_num_dict[NEGNUM] += 1
                elif negativeemo_count < positiveemo_count:
                    emo_num_dict[POSNUM] += 1
                elif negativeemo_count == positiveemo_count and positiveemo_count != 0:
                    emo_num_dict[EQUNUM] += 1
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