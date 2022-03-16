import os
import time
"""
suggest to use python3.8
Install package: C:\python38>python.exe -m pip install xlrd
"""

# All configuration items in the program are in this file

'''Global Parameters'''
DEBUG = False  # debug mode
VISUAL = False  # Visualization
VISUAL_SAVE = True

# data files
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