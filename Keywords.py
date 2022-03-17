# -*- coding:utf-8 -*-
import jieba
import pickle
import multiprocessing
import threading
from wordcloud import WordCloud

from Config import *


# Customize threads and return analysis values,
# use Manager to communicate between processes.
def extractOneWord(one_data):
    temp_dict = {}
    try:
        if KEY_ANALUSIS_MODE == TFIDF:
            keywords = jieba.analyse.extract_tags(
                one_data[ARRAYID['content']], topK=KEY_NUMS, withWeight=False, allowPOS=())
        elif KEY_ANALUSIS_MODE == TEXTRANK:
            keywords = jieba.analyse.textrank(
                one_data[ARRAYID['content']], topK=KEY_NUMS, withWeight=False, allowPOS=())
        temp_dict[one_data[ARRAYID['docid']]] = keywords
    except Exception as e:
        temp_dict[one_data[ARRAYID['docid']]] = []
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

def thread_analysis(split_dataset, allkey_dict):
    thread_list = []
    for each in split_dataset:
        t = KeyThread(extractOneWord, args=(each, ))
        t.setDaemon(True)
        t.start()
        thread_list.append(t)
    for one in thread_list:
        one.join()
        result = one.get_result()
        for k, v in result.items():
            allkey_dict[k] = v

# Extract the first n keywords of content (default 3)
def extractAllKeywords(dataset, keynums, analysis_allkey_filename):
    if not os.path.exists(analysis_allkey_filename):
        if MULTI_MODE:
            print('[{}] This is the first time for keyword extraction in multiprocessing mode. (30min) ...'.format(TIME()))
            cpu_cnt = multiprocessing.cpu_count()
            each_datalen = int(len(dataset) / cpu_cnt)
            # print(len(dataset), each_datalen, cpu_cnt)

            allkey_dict = multiprocessing.Manager().dict()
            process_list = []
            for i in range(cpu_cnt):
                print("{} / {}".format(each_datalen*i, each_datalen*(i+1)))
                if i == cpu_cnt - 1:
                    p = multiprocessing.Process(target=thread_analysis, args=(dataset[each_datalen*i:], allkey_dict, ))  # 实例化进程对象
                else:
                    p = multiprocessing.Process(target=thread_analysis, args=(dataset[each_datalen*i:each_datalen*(i+1)], allkey_dict, ))  # 实例化进程对象
                p.daemon = True
                p.start()
                process_list.append(p)
            for one in process_list:
                one.join()
            allkey_dict = dict(allkey_dict)
        else:
            print('[{}] This is the first time for keyword extraction(#->1000) (1h) ...'.format(TIME()))
            allkey_dict = {}
            for i, v in enumerate(dataset):
                try:
                    if KEY_ANALUSIS_MODE == TFIDF:
                        keywords = jieba.analyse.extract_tags(
                            v[ARRAYID['content']], topK=keynums, withWeight=False, allowPOS=())
                    elif KEY_ANALUSIS_MODE == TEXTRANK:
                        keywords = jieba.analyse.textrank(
                            v[ARRAYID['content']], topK=keynums, withWeight=False, allowPOS=())
                    if len(keywords) > 0:
                        allkey_dict[v[ARRAYID['docid']]] = keywords
                    else:
                        allkey_dict[v[ARRAYID['docid']]] = []
                    if i % 40000 == 0:
                        print("\n{} / {}  ".format(i, len(dataset)), end="")
                    if i % 1000 == 0:
                        print("#", end="")
                except Exception as e:
                    allkey_dict[v[ARRAYID['docid']]] = []

        print('[{}] The length after analysis is {}. ...'.format(TIME(), len(allkey_dict)))
        with open(analysis_allkey_filename, 'wb') as file:  # Save analysis results.
            pickle.dump(allkey_dict, file)
        print()


# Keywords are retrieved according to docid, no longer using location, more accurate.
def extractNKeywords(allkey_dict, nkey):
    nkey_dict = {}
    wordcloudmap = {}
    for k, v in allkey_dict.items():
        temp_key = []
        nnum = 0
        for one in v:
            if one not in KEY_STOP_WORDS:
                temp_key.append(one)
                nnum += 1
                if one not in wordcloudmap:
                    wordcloudmap[one] = 1
                else:
                    wordcloudmap[one] += 1
            if nnum >= nkey:
                break
        nkey_dict[k] = temp_key

    # Extracting the top n ranked terms.
    wordcloudlist = []
    for _ in range(KEY_CLOUDNUM):
        temp_cloud = max(wordcloudmap, key=wordcloudmap.get)
        wordcloudlist.append(temp_cloud)
        wordcloudmap.pop(temp_cloud)

    return nkey_dict, wordcloudlist


# For analysing and processing of data
def visWordCloud(wordcloudlist):
    wl = " ".join(wordcloudlist)
    # Setting parameters
    wordcloud = WordCloud(
        background_color='white',  # Background color
        max_words=KEY_CLOUDNUM,  # Maximum number of words to displayed
        max_font_size=100,  # Setting maximum font size of word
        font_path='C:/Windows/Fonts/msyhbd.ttc',  # set fonts
        width=2000,
        height=1500,
        random_state=30,  # Set how many randomly generated states i.e.no. of color to display
        # scale=.5
    ).generate(wl)
    # show wordcloud
    wordcloud.to_file(KEY_CLOUD_PATH)  # save wordcloud