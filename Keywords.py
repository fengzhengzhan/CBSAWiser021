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
        if VISUAL:
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.show()

        wordcloud.to_file(KEY_CLOUD_PATH)  # save wordcloud


# Extracting the source of keywords
# Linking sources to docid
def extractSourceKeywords(dataset):
    source_key_dict: 'dict[str:set]' = {}
    for one in dataset[1:]:
        authortype = one[ARRAYID['author_type']]
        if authortype == '':
            authortype = "匿名"
        id = one[ARRAYID['docid']]
        if authortype not in source_key_dict:
            source_key_dict[authortype] = set()
        source_key_dict[authortype].add(id)
    return source_key_dict


# Plotting the percentage of speech in each camp according to the timeline
def visSourceTime(dataset, source_list):
    if VISUAL_SAVE:
        first_date, second_date = None, None
        dt = datetime.timedelta(days=KEY_SOURCETIME_INTERVAL)
        plt_list = [source_list]
        day_num = []
        # Init the dict of source numbers.
        source_num_dict = {}
        for each in source_list:
            source_num_dict[each] = 0
        # data loop
        for i in range(0, len(dataset)):
            # Time analysis
            now_date = dataset[i][ARRAYID['pubdate']]
            # Determine if it is a time type
            if isinstance(now_date, datetime.datetime):
                if first_date is None:  # First time assignment
                    temp_date = str(now_date.year) + "-" + str(now_date.month) + "-" + str(now_date.day)
                    first_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")
                    second_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d") + dt
                    # print(first_date, second_date)
                # Determine time range
                if first_date <= now_date <= second_date and i != len(dataset) - 1:
                    authortype = dataset[i][ARRAYID['author_type']]
                    if authortype == '':
                        authortype = "匿名"
                    source_num_dict[authortype] += 1
                else:
                    temp_num = []
                    for one in source_list:
                        temp_num.append(source_num_dict[one])
                    plt_list.append(temp_num)
                    day_num.append(str(second_date)[2:4]+str(second_date)[5:7]+str(second_date)[8:10])
                    # Init the dict of source numbers。
                    source_num_dict = {}
                    for each in source_list:
                        source_num_dict[each] = 0
                    first_date = second_date
                    second_date = second_date + dt

        # print(plt_list)
        # Folding Line Chart
        plt.figure(figsize=(16, 8))
        ax = plt.gca()
        x = day_num
        # print(len(x))
        for sourcei in range(len(source_list)):
            temp_line = []
            for onej in range(1, len(plt_list)):
                temp_line.append(plt_list[onej][sourcei])
            plt.plot(x, temp_line, label=source_list[sourcei])
        ax.set_xticks(x)
        ax.set_xticklabels(x, rotation=40)
        x_major_locator = MultipleLocator(int(len(day_num) / 12))
        ax.xaxis.set_major_locator(x_major_locator)
        plt.xlabel("Number of Comments")  # Horizontal coordinate name
        plt.ylabel("Comments interval")  # Vertical coordinate name
        myfont = fm.FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
        plt.legend(loc="best", prop=myfont)  # Figure legend
        plt.savefig(KEY_VIS_SOURCE_PATH)
        if VISUAL:
            plt.show()
