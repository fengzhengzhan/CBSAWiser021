# -*- coding:utf-8 -*-
import jieba
import pickle
import multiprocessing
import threading

from Config import *


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

# Customize threads and return analysis values,
# use Manager to communicate between processes.
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

def thread_analysis(split_dataset, nkey_dict):
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
            nkey_dict[k] = v


# Extract the first n keywords of content (default 3)
def extractNKeywords(dataset, nkey, analysis_nkey_filename):
    if not os.path.exists(analysis_nkey_filename):
        if MULTI_MODE:
            print('[{}] This is the first time for keyword extraction in multiprocessing mode. (30min) ...'.format(TIME()))
            cpu_cnt = multiprocessing.cpu_count()
            each_datalen = int(len(dataset) / cpu_cnt)
            # print(len(dataset), each_datalen, cpu_cnt)

            nkey_dict = multiprocessing.Manager().dict()
            process_list = []
            for i in range(cpu_cnt):
                print("{} / {}".format(each_datalen*i, each_datalen*(i+1)))
                if i == cpu_cnt - 1:
                    p = multiprocessing.Process(target=thread_analysis, args=(dataset[each_datalen*i:], nkey_dict, ))  # 实例化进程对象
                else:
                    p = multiprocessing.Process(target=thread_analysis, args=(dataset[each_datalen*i:each_datalen*(i+1)], nkey_dict, ))  # 实例化进程对象
                p.daemon = True
                p.start()
                process_list.append(p)
            for one in process_list:
                one.join()
            nkey_dict = dict(nkey_dict)
        else:
            print('[{}] This is the first time for keyword extraction(#->1000) (1h) ...'.format(TIME()))
            nkey_dict = {}
            for i, v in enumerate(dataset):
                try:
                    if KEY_ANALUSIS_MODE == TFIDF:
                        keywords = jieba.analyse.extract_tags(
                            v[ARRAYID['content']], topK=nkey, withWeight=False, allowPOS=())
                    elif KEY_ANALUSIS_MODE == TEXTRANK:
                        keywords = jieba.analyse.textrank(
                            v[ARRAYID['content']], topK=nkey, withWeight=False, allowPOS=())
                    if len(keywords) > 0:
                        nkey_dict[v[ARRAYID['docid']]] = keywords
                    else:
                        nkey_dict[v[ARRAYID['docid']]] = []
                    if i % 40000 == 0:
                        print("\n{} / {}  ".format(i, len(dataset)), end="")
                    if i % 1000 == 0:
                        print("#", end="")
                except Exception as e:
                    nkey_dict[v[ARRAYID['docid']]] = []

        print('[{}] The length after analysis is {}. ...'.format(TIME(), len(nkey_dict)))
        with open(analysis_nkey_filename, 'wb') as file:  # Save analysis results.
            pickle.dump(nkey_dict, file)
        print()


# For analysing and processing of data
def visWordCloud(dataset):
    content = []
    for data in dataset:
        content.append(data[ARRAYID['content']])
    content = content[1:]  # Remove the first row of table headers
    # Construct word cloud
    print("[{}] Word cloud analysis in progress ...".format(TIME()))
    text = ""
    for i, w in enumerate(content):
        try:
            keywords = jieba.analyse.extract_tags(w, topK=1, withWeight=False, allowPOS=())
            if len(keywords) > 0:
                text += str(keywords[0])
            if i % 40000 == 0:
                print("\n{} / {}  ".format(i, len(content)), end="")
            if i % 1000 == 0:
                print("#", end="")
        except Exception as e:
            pass
    # jieba word separation
    wordlist = jieba.cut(text, cut_all=True)
    wl = " ".join(wordlist)
    # Setting parameters
    wordcloud = WordCloud(
        background_color='white',  # Background color
        max_words=1000,  # Maximum number of words to displayed
        stopwords=STOPWORDS,  # Setting stopwords
        max_font_size=100,  # Setting maximum font size of word
        font_path='C:/Windows/Fonts/msyhbd.ttc',  # Setting the font
        width=2000,
        height=1500,
        random_state=30,  # Set how many randomly generated states i.e.no. of color to display
        # scale=.5
    ).generate(wl)
    # show word cloud
    plt.imshow(wordcloud)
    # show x,y-axis or not
    plt.axis("off")
    plt.show()
    # show wordcloud
    wordcloud.to_file('analysis.png')  # save wordcloud