# -*- coding:utf-8 -*-
import jieba.analyse
import pickle
import multiprocessing
import threading
from wordcloud import WordCloud
import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.pyplot import MultipleLocator

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
def extractAllKeywords(dataset, analysis_allkey_filename):
    if not os.path.exists(analysis_allkey_filename):
        if MULTI_MODE:
            print('[{}] This is the first time for keyword extraction in multiprocessing mode ...'.format(TIME()))
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
            print('[{}] This is the first time for keyword extraction(#->1000) ...'.format(TIME()))
            allkey_dict = {}
            for i, v in enumerate(dataset):
                try:
                    if KEY_ANALUSIS_MODE == TFIDF:
                        keywords = jieba.analyse.extract_tags(
                            v[ARRAYID['content']], topK=KEY_NUMS, withWeight=False, allowPOS=())
                    elif KEY_ANALUSIS_MODE == TEXTRANK:
                        keywords = jieba.analyse.textrank(
                            v[ARRAYID['content']], topK=KEY_NUMS, withWeight=False, allowPOS=())
                    if len(keywords) > 0:
                        allkey_dict[v[ARRAYID['docid']]] = keywords
                    else:
                        allkey_dict[v[ARRAYID['docid']]] = []
                    if i % 40000 == 0:
                        print("\n{} / {}  ".format(i, len(dataset)), end="")
                    if i % 1000 == 0:
                        print("#", end="")
                except Exception as e:
                    print(e)
                    allkey_dict[v[ARRAYID['docid']]] = []

        print()
        print('[{}] The length after analysis is {}. ...'.format(TIME(), len(allkey_dict)))
        with open(analysis_allkey_filename, 'wb') as file:  # Save analysis results.
            pickle.dump(allkey_dict, file)


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
    wordclouddict = {}
    for _ in range(KEY_CLOUDNUM):
        temp_cloud = max(wordcloudmap, key=wordcloudmap.get)
        wordclouddict[temp_cloud] = wordcloudmap[temp_cloud]
        wordcloudmap.pop(temp_cloud)
    return nkey_dict, wordclouddict


# For analysing and processing of data
def visWordCloud(wordclouddict):
    if VISUAL_SAVE:
        # Setting parameters
        wordcloud = WordCloud(
            background_color='white',  # Background color
            max_words=KEY_CLOUDNUM,  # Maximum number of words to displayed
            min_font_size=4,
            max_font_size=None,  # Setting maximum font size of word
            font_path='C:/Windows/Fonts/msyh.ttc',  # set fonts
            width=2000,
            height=1500,
            random_state=50,  # Set how many randomly generated states i.e.no. of color to display
            # scale=.5
        ).generate_from_frequencies(wordclouddict)
        # show wordcloud
        if VISUAL_SHOW:
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.show()

        wordcloud.to_file(KEY_CLOUD_PATH)  # save wordcloud


# Extracting the author/publisher of keywords
# Linking author/publisher to docid
def extractInterestingKeywords(dataset, coolid):
    key_dict: 'dict[str:set]' = {}
    for one in dataset[1:]:
        type = one[coolid]
        if type == '':
            type = "匿名"
        id = one[ARRAYID['docid']]
        if type not in key_dict:
            key_dict[type] = set()
        key_dict[type].add(id)
    return key_dict


# Plotting the percentage of speech in each camp according to the timeline
def timeDataAnalysis(dataset, data_list, coolid, day_interval):
    first_date = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
    second_date = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
    dt = datetime.timedelta(days=day_interval)
    day_list = []
    time_data_list = [data_list, ]  # Corresponding quantities sorted by time
    time_id_list = [data_list, ]

    # Init the dict of data numbers.
    data_num_dict = {}
    data_id_dict = {}
    for each in data_list:
        data_num_dict[each] = 0
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
            if first_date is None:  # First time assignment
                temp_date = str(now_date.year) + "-" + str(now_date.month) + "-" + str(now_date.day)
                first_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")
                second_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d") + dt
                # print(first_date, second_date)
            # Determine time range
            if i < len(dataset) and first_date <= now_date <= second_date:
                type = dataset[i][coolid]
                if type == '':
                    type = "匿名"
                data_num_dict[type] += 1
                data_id_dict[type].append(dataset[i][ARRAYID['docid']])
            else:
                temp_num = []
                temp_id = []
                for one in data_list:
                    temp_num.append(data_num_dict[one])  # Guarantee order
                    temp_id.append(data_id_dict[one])
                time_data_list.append(temp_num)
                time_id_list.append(temp_id)
                day_list.append(str(second_date)[0:4]+str(second_date)[5:7]+str(second_date)[8:10])
                # Init the dict of data numbers。
                data_num_dict = {}
                data_id_dict = {}
                for each in data_list:
                    data_num_dict[each] = 0
                    data_id_dict[each] = []
                first_date = second_date
                second_date = second_date + dt
                print(second_date, "--------", dt)
                if i < len(dataset):
                    i -= 1

    return day_list, time_data_list, time_id_list

# visualized data
def visTimeData(x_data, y_data, curves_num, title, data_path):
    if VISUAL_SAVE:
        # print(plt_list)
        # Folding Line Chart
        plt.figure(figsize=(16, 8))
        ax = plt.gca()
        x = x_data  # day_list
        # print(len(x))
        for datai in range(len(curves_num)):
            y = []
            for dayj in range(1, len(y_data)):  # Skip start time
                y.append(y_data[dayj][datai])
            plt.plot(x, y, label=curves_num[datai])
        ax.set_xticks(x)
        ax.set_xticklabels(x, rotation=40)
        x_major_locator = MultipleLocator(int(len(x_data) / 12))
        ax.xaxis.set_major_locator(x_major_locator)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        myfont = fm.FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
        plt.title(title, fontdict={'weight': 'bold', 'size': 20})
        plt.xlabel("Number of Comments")  # Horizontal coordinate name
        plt.ylabel("Comments interval")  # Vertical coordinate name
        plt.legend(loc="best", prop=myfont)  # Figure legend
        plt.savefig(data_path)
        if VISUAL_SHOW:
            plt.show()
