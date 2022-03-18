# -*- coding:utf-8 -*-
import os
import time
"""
suggest to use python3.8
Install package: C:\python38>python.exe -m pip install xlrd==1.2.0
pip install numpy matplotlib pillow wordcloud imageio jieba snownlp itchat -i https://pypi.tuna.tsinghua.edu.cn/simple
"""

# All configuration items in the program are in this file

'''Global Parameters'''
DEBUG = False  # debug mode
VISUAL = False  # Visualization
VISUAL_SAVE = True
MULTI_MODE = False  # Multiprocessing extract key words

ARRAYID = {'docid':0, 'comment_count':1, 'like_count':2, 'dislike_count':3, 'love_count':4, 'haha_count':5, 'wow_count':6, 'angry_count':7, 'sad_count':8, 'share_count':9, 'view_count':10, 'negativeemo_count':11, 'positiveemo_count':12, 'influence_count':13, 'headline':14, 'author*':15, 'pubname':16, 'pubdate':17, 'region':18, 'fans_count':19, 'author_type':20, 'content':21}  # 字典 便于访问字段对应的列
TIME = lambda :time.strftime('%H:%M:%S',time.localtime(time.time()))  # Anonymous function to return the time. TIME()
file_time = str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())))


'''Preprocessing'''
PRESTR = "1 Preprocessing"
DATA_PATH = "data"
ANALYSIS_PATH = "analysis"
DATA_FILENAME = DATA_PATH + os.sep + "new_analytics_challenge_dataset_edited.xlsx"
DATA_SAVE_FILENAME = DATA_PATH + os.sep + "new_analytics_challenge_dataset_edited.pkl"
PRE_ID_CONT = ['2020021100002988743', '2020021100000087375']

'''Keywords'''
KEYSTR = "2 Keywords"
KEY_NUMS = 12  # Number of alternative analytic words for easy processing during analysis.
KEY_NKEY_FILENAME = ANALYSIS_PATH + os.sep + "keywords_nkey_dict.pkl"
# Keyword Extraction Algorithm
TFIDF = 'TF-IDF'
TEXTRANK = 'TextRank'
KEY_ANALUSIS_MODE = TFIDF  # TFIDF  TEXTRANK
KEY_NKEY = 3  # the number of keywords to be extracted
KEY_CLOUDNUM = 50  # Number of words drawn by the word cloud.
KEY_CLOUD_PATH = ANALYSIS_PATH + os.sep + file_time + "wordcloud.png"
KEY_SOURCETIME_INTERVAL = 7  # Discourse source analysis interval.
KEY_VIS_SOURCE_PATH = ANALYSIS_PATH + os.sep + file_time + "sourcetime.jpg"

KEY_STOP_WORDS = []
with open("StopWords.txt", 'r', encoding="utf-8") as f:
    for line in f:
        KEY_STOP_WORDS.append(line.replace('\n', ''))

if DEBUG:
    DATA_FILENAME = DATA_PATH + os.sep + "test.xlsx"
    DATA_SAVE_FILENAME = DATA_PATH + os.sep + "test.pkl"
    KEY_NKEY_FILENAME = ANALYSIS_PATH + os.sep + "nkey_test.pkl"

'''Emotion'''
INTERESTING_WORDS = ['醫護']  # extract content related to respective keywords  (\\ represent null)
INTERESTING_CONTENT_FILENAME = ANALYSIS_PATH + os.sep + file_time + "content_analysis.txt"
INTERESTING_TEXT = ""


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