# -*- coding:utf-8 -*-
import xlrd
import time
import pickle
import os
import matplotlib.pyplot as plt
# from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
import jieba.analyse
import numpy as np
from PIL import Image
import datetime
import math

'''
suggest to use python3
install package ->  pip3 install -r requirements.txt
'''

DEBUG = False
DATA_PATH = "data"
ANALYSIS_PATH = "analysis"
DATA_FILENAME = DATA_PATH + os.sep + "new_analytics_challenge_dataset_edited.xlsx"
DATA_SAVE_FILENAME = DATA_PATH + os.sep + "new_analytics_challenge_dataset_edited.pkl"
ANALYSIS_NKEY_FILENAME = ANALYSIS_PATH + os.sep + "analysis_nkey_array.pkl"

ARRAYID = {'docid':0, 'comment_count':1, 'like_count':2, 'dislike_count':3, 'love_count':4, 'haha_count':5, 'wow_count':6, 'angry_count':7, 'sad_count':8, 'share_count':9, 'view_count':10, 'negativeemo_count':11, 'positiveemo_count':12, 'influence_count':13, 'headline':14, 'author*':15, 'pubname':16, 'pubdate':17, 'region':18, 'fans_count':19, 'author_type':20, 'content':21}  # 字典 便于访问字段对应的列
TIME = lambda :time.strftime('%H:%M:%S',time.localtime(time.time()))  # Anonymous function to return the time
file_time = str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())))

REMOVE_WORDS = ['https', 'com', 'did', 'http', '01', 'bit', '', 'www', '10', '11', '12', '14', '23', '...', 'E6%', 'D100', 'was', '精液', 'light', 'small', '武漢', '確診', '醫生', '香港', '抗疫', '肺炎', '中國', '疫情', '防疫', '我們', '港人', '醫院', '美國', '檢測', '新冠', '疫苗', '接種', 'face', '英國', 'Shared', 'Hong', '病毒', '台灣', '你們', '一個', '個案', '點新聞', '甚麼', '新聞', '他們', '大學生', '政府', '國家', '蘋果', '英文', ' 最佳', '這句', '因為', '毛記', 'dotdotnews']  # 剔除词汇
INTERESTING_WORDS = ['醫護']  # extract content related to respective keywords  (\\ represent null)
INTERESTING_CONTENT_FILENAME = ANALYSIS_PATH + os.sep + file_time + "content_analysis.txt"
INTERESTING_TEXT = ""

NKEY = 3  # the number of keywords to be extracted
# Analysis by time
TIME_MODE = "time_mode"
TIME_INTERVAL = 30  # days interval of analysis
EACH_LINE_KEYWORDS = 1  # Number of keywords extracted from each line of data  Range:1-3
EACH_WEEKEND_N = 12  # Number of keywords extracted each week
ENABLE_TIME_WEIGHT = True  # Whether to allow weighting, only return the results that have specified keyword(s)
TIME_TXT_FILENAME = ANALYSIS_PATH + os.sep + file_time + "time_analysis.txt"
# Emotion analysis
EMO_MODE = "emo_mode"
ZEROEQUNUM = 'zeroequnum' # Result displayed
EQUNUM = 'equnum'
POSNUM = 'posnum'
NEGNUM = 'negnum'
ZEROEQU = 'zeroequ'
EQU = 'equ'
POS = 'pos'
NEG = 'neg'
EMO_EACH_LINE = 1  # Number of keywords extracted from each line of data  Range:1-3
EACH_EMO_N = 50
ENABLE_EMO_WEIGHT = True  # Whether to allow weighting, only return the results that have specified keyword(s)
EMO_TXT_FILENAME = ANALYSIS_PATH + os.sep + file_time + "emo_analysis.txt"


# Conditional Analysis
TIME_ANALYSIS = "timeAnalysis"
EMOTION_ANALYSIS = "emotionAnalysis"



if DEBUG:
    DATA_FILENAME = DATA_PATH + os.sep + "test.xlsx"
    DATA_SAVE_FILENAME = DATA_PATH + os.sep + "test.pkl"
    ANALYSIS_NKEY_FILENAME = ANALYSIS_PATH + os.sep + "nkey_test.pkl"

# Environment preparation, file creation
def readyEnv():
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    if not os.path.exists(ANALYSIS_PATH):
        os.mkdir(ANALYSIS_PATH)
    if not os.path.isfile(DATA_FILENAME):
        raise Exception("没有数据文件，请将数据文件拷贝到data目录下")

# Save data as pkl Increase speed on further processing
def excelToPickle(filename=DATA_FILENAME, save_filename=DATA_SAVE_FILENAME):
    if not os.path.exists(save_filename):  # Data conversion will not be performed if the pkl file exists
        print('[{}] This is the first read, file conversion in progress (3min) ...'.format(TIME()))
        xlsx = xlrd.open_workbook(filename)  # Open the workbook, the first time of reading the file takes ard 2 mins
        temp_array = []
        for sh in xlsx.sheets():  # Traversing data to save to an array
            for r in range(sh.nrows):
                temp_data = sh.row_values(r)
                try:
                    # Convert time to datetime format
                    temp_data[ARRAYID['pubdate']] = xlrd.xldate.xldate_as_datetime(temp_data[ARRAYID['pubdate']], 0)
                except Exception as e:
                    pass
                temp_array.append(temp_data)

        with open(save_filename, 'wb') as file:  # Save data as pkl Increase speed on further processing
            pickle.dump(temp_array, file)

# Read pkl rile
def readPklFile(filename):
    with open(filename, 'rb') as file:
        temp = pickle.load(file)
    return temp


# For analysing and processing of data
def gainWordCloud(dataset):
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

# Extract the first n keywords of content (default 3)
def extractNKeywords(dataset, nkey=NKEY, analysis_nkey_filename=ANALYSIS_NKEY_FILENAME):
    if not os.path.exists(analysis_nkey_filename):
        print('[{}] This is the first time for keyword extraction(#->1000) (2h) ...'.format(TIME()))
        nkey_array = []
        for i, v in enumerate(dataset):
            try:
                keywords = jieba.analyse.extract_tags(v[ARRAYID['content']], topK=nkey, withWeight=False, allowPOS=())
                if len(keywords) > 0:
                    nkey_array.append(keywords)
                else:
                    nkey_array.append([''])
                if i % 40000 == 0:
                    print("\n{} / {}  ".format(i, len(dataset)), end="")
                if i % 1000 == 0:
                    print("#", end="")
            except Exception as e:
                nkey_array.append([''])

        with open(analysis_nkey_filename, 'wb') as file:  # 保存分析结果
            pickle.dump(nkey_array, file)
        print()

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
                        timetext += extrectAnalysisKeyWords(TIME_MODE, time_dict, EACH_WEEKEND_N, REMOVE_WORDS, ENABLE_TIME_WEIGHT)
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
                        emotext += extrectAnalysisKeyWords(EMO_MODE, emov, EACH_EMO_N, REMOVE_WORDS, ENABLE_EMO_WEIGHT)
                        emotext += "\n"
                    saveToTxt(emotext, EMO_TXT_FILENAME)

            # Show progress of processing
            if i % 80000 == 0:
                print("\n{} / {}  ".format(i, len(dataset)), end="")
            if i % 1000 == 0:
                print("#", end="")


def mainAnalysis():
    print(" ----------- Start of data analysis ----------- ")

    readyEnv()
    excelToPickle()
    print('[{}] File reading in progress (6s) ...'.format(TIME()))
    dataset = readPklFile(DATA_SAVE_FILENAME)  # This function reads data in excel and returns the file data in 6s
    print('[{}] Keyword extraction of data ...'.format(TIME()))
    extractNKeywords(dataset)
    print('[{}] Read keyword information ...'.format(TIME()))
    nkey_array = readPklFile(ANALYSIS_NKEY_FILENAME)  # Keyword file reading
    print('[{}] File reading completed. len_dataset:{} <-> len_nkey_array:{} ...'.format(TIME(), len(dataset), len(nkey_array)))
    if len(dataset) != len(nkey_array):
        raise Exception("数据处理出现错误，长度不一致！")
    # print('[{}] Word cloud analysis of data ...'.format(TIME()))
    # gainWordCloud(dataset)

    # dataset sort according to time
    # 1. Keyword analysis by time ()
    print('[{}] Step 1: Time analysis of data ...'.format(TIME()))
    print('[{}] Step 2: Emotion analysis of data ...'.format(TIME()))
    print('[{}] Step 3: Keyword extraction and filtering ...'.format(TIME()))
    conditionAnalysis(dataset, nkey_array, [TIME_ANALYSIS, EMOTION_ANALYSIS])

    print("\n", '[{}] Keyword Time Analysis ...'.format(TIME()))
    print(INTERESTING_TEXT)

    print(" ----------- End of data analysis ----------- ")


if __name__ == '__main__':
    mainAnalysis()
