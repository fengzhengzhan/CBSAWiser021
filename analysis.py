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
建议使用python3
安装依赖包  pip3 install -r requirements.txt
'''


'''
普通函数：首字母小写  驼峰  exampleFunction
全局变量名：大写字母  _分割  EXAMPLE_VARIABLE
普通变量： 小写字母 _分割  example_variable_common
文件名：特殊情况外短名字全小写(变量名)
文件夹：大写字母开头(类名)
'''

# 大写所有的全局变量
DEBUG = False  # 取前100条保存成test.xlsx
DATA_PATH = "data"
ANALYSIS_PATH = "analysis"
DATA_FILENAME = DATA_PATH + os.sep + "new_analytics_challenge_dataset_edited.xlsx"
DATA_SAVE_FILENAME = DATA_PATH + os.sep + "new_analytics_challenge_dataset_edited.pkl"
ANALYSIS_NKEY_FILENAME = ANALYSIS_PATH + os.sep + "analysis_nkey_array.pkl"

ARRAYID = {'docid':0, 'comment_count':1, 'like_count':2, 'dislike_count':3, 'love_count':4, 'haha_count':5, 'wow_count':6, 'angry_count':7, 'sad_count':8, 'share_count':9, 'view_count':10, 'negativeemo_count':11, 'positiveemo_count':12, 'influence_count':13, 'headline':14, 'author*':15, 'pubname':16, 'pubdate':17, 'region':18, 'fans_count':19, 'author_type':20, 'content':21}  # 字典 便于访问字段对应的列
TIME = lambda : time.strftime('%H:%M:%S', time.localtime(time.time()))  # 匿名函数 用于返回时间
file_time = str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())))

REMOVE_WORDS = ['https', 'com', 'did', 'http', '01', 'bit', '', 'www', '10', '11', '12', '14', '23', '...', 'E6%', 'D100', 'was', '精液', 'light', 'small', '口罩', '武漢', '確診', '醫生', '香港', '抗疫', '肺炎', '中國', '疫情', '防疫', '我們', '港人', '醫院', '美國', '檢測', '新冠', '疫苗', '接種', 'face', '英國', 'Shared', '醫護', 'Hong', '病毒', '隔離', '台灣', '你們', '一個', '個案', '抽獎', '政府', '國家']  # 剔除词汇
INTERESTING_WORDS = ['特朗普', '抽獎']  # 关键词提取对应的内容  (\\代表空白字符)
INTERESTING_CONTENT_FILENAME = ANALYSIS_PATH + os.sep + file_time + "content_analysis.txt"
INTERESTING_TEXT = ""

NKEY = 3  # 提取关键词个数
# 时间分析
TIME_MODE = "time_mode"
TIME_INTERVAL = 6  # 天数间隔
EACH_LINE_KEYWORDS = 1  # 每一条数据选取几个关键词  范围:1-3
EACH_WEEKEND_N = 12  # 每周提取多少个关键词
ENABLE_TIME_WEIGHT = True  # 是否允许权重(数量)
TIME_TXT_FILENAME = ANALYSIS_PATH + os.sep + file_time + "time_analysis.txt"
# 情感分析
EMO_MODE = "emo_mode"
ZEROEQUNUM = 'zeroequnum'  # 统计数据
EQUNUM = 'equnum'
POSNUM = 'posnum'
NEGNUM = 'negnum'
ZEROEQU = 'zeroequ'
EQU = 'equ'
POS = 'pos'
NEG = 'neg'
EMO_EACH_LINE = 1  # 每一条数据选取几个关键词  范围:1-3
EACH_EMO_N = 50
ENABLE_EMO_WEIGHT = True  # 是否允许权重
EMO_TXT_FILENAME = ANALYSIS_PATH + os.sep + file_time + "emo_analysis.txt"

# 条件分析类别
TIME_ANALYSIS = "timeAnalysis"
EMOTION_ANALYSIS = "emotionAnalysis"

if DEBUG:
    DATA_FILENAME = DATA_PATH + os.sep + "test.xlsx"
    DATA_SAVE_FILENAME = DATA_PATH + os.sep + "test.pkl"
    ANALYSIS_NKEY_FILENAME = ANALYSIS_PATH + os.sep + "nkey_test.pkl"


# 环境准备，创建文件夹
def readyEnv():
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    if not os.path.exists(ANALYSIS_PATH):
        os.mkdir(ANALYSIS_PATH)
    if not os.path.isfile(DATA_FILENAME):
        raise Exception("没有数据文件，请将数据文件拷贝到data目录下")

# 将数据保存为pkl 增加二次读取时的速度
# [[docid, comment_count, ...],[2020021100002988743, 0, 0, ...],[2020021100000087375, 0, 0, ...]]
def excelToPickle(filename=DATA_FILENAME, save_filename=DATA_SAVE_FILENAME):
    if not os.path.exists(save_filename):  # pkl文件存在则不执行数据转换
        print('[{}] This is the first read, file conversion in progress (3min) ...'.format(TIME()))
        xlsx = xlrd.open_workbook(filename)  # 打开文件 第一次文件读取时间较长大约在2分钟左右
        temp_array = []
        for sh in xlsx.sheets():  # 遍历数据保存至数组
            for r in range(sh.nrows):
                temp_data = sh.row_values(r)
                try:
                    # 时间转换成datetime类型
                    temp_data[ARRAYID['pubdate']] = xlrd.xldate.xldate_as_datetime(temp_data[ARRAYID['pubdate']], 0)
                except Exception as e:
                    pass
                temp_array.append(temp_data)

        with open(save_filename, 'wb') as file:  # 保存为pkl文件，增加读取速度
            pickle.dump(temp_array, file)

# 读取pkl文件
def readPklFile(filename):
    with open(filename, 'rb') as file:
        temp = pickle.load(file)
    return temp


# 用于分析处理数据  未使用
def gainWordCloud(dataset):
    content = []
    for data in dataset:
        content.append(data[ARRAYID['content']])
    content = content[1:]  # 去掉第一行表头数据
    # 构建词云
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
    # jieba分词
    wordlist = jieba.cut(text, cut_all=True)
    wl = " ".join(wordlist)
    # 设置参数
    wordcloud = WordCloud(
        background_color='white',  # 背景颜色
        max_words=1000,  # 设置最多现实的词数
        stopwords=STOPWORDS,  # 设置停用词
        max_font_size=100,  # 设置字体最大值
        font_path='C:/Windows/Fonts/msyhbd.ttc',  # 设置字体，路径在电脑内
        width=2000,
        height=1500,
        random_state=30,  # 设置有多少种随机生成状态，即有多少种配色方案
        # scale=.5
    ).generate(wl)
    # 展示词云
    plt.imshow(wordcloud)
    # 是否显示想x，y坐标
    plt.axis("off")
    plt.show()
    # 写入文件
    wordcloud.to_file('analysis.png')  # 把词云保存下

# 提取content前n个关键词 (默认3)
def extractNKeywords(dataset, nkey=NKEY, analysis_nkey_filename=ANALYSIS_NKEY_FILENAME):
    if not os.path.exists(analysis_nkey_filename):
        print('[{}] This is the first time for keyword extraction(#->1000) (2h) ...'.format(TIME()))
        nkey_array = []
        for i, v in enumerate(dataset):  # []
            try:
                keywords = jieba.analyse.extract_tags(v[ARRAYID['content']], topK=nkey, withWeight=False, allowPOS=())  # 使用jieba库分析关键词
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

# 数据展示保存
def saveToTxt(text, filename):
    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(text)
        f.write("\n")

# 关键词提取，并保存
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


# 遍历数据，进行条件分析
def conditionAnalysis(dataset, nkey_array, mode):
    if mode:
        # 时间分析
        first_date, second_date = None, None  # 滚动赋值  None NULL nul 空值
        dt = datetime.timedelta(days=TIME_INTERVAL)
        time_dict = {}
        # 情感分析
        emo_num_dict = {ZEROEQUNUM:0, EQUNUM:0, POSNUM:0, NEGNUM:0}
        emo_dict = {ZEROEQU: {}, EQU:{}, POS:{}, NEG:{}}

        # 数据循环
        for i in range(0, len(dataset)):
            # 时间分析
            if TIME_ANALYSIS in mode:
                now_date = dataset[i][ARRAYID['pubdate']]
                # 判断是否是时间类型
                if isinstance(now_date, datetime.datetime):
                    if first_date is None:  # 第一次时间赋值
                        temp_date = str(now_date.year)+"-"+str(now_date.month)+"-"+str(now_date.day)
                        first_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")
                        second_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")+dt
                        # print(first_date, second_date)
                    # 判断时间范围
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
                        # 查找每周评论走向
                        timetext = str(first_date.strftime("%Y-%m-%d-%H:%M:%S")) + "->" + str(second_date.strftime("%Y-%m-%d-%H:%M:%S"))
                        timetext += extrectAnalysisKeyWords(TIME_MODE, time_dict, EACH_WEEKEND_N, REMOVE_WORDS, ENABLE_TIME_WEIGHT)
                        saveToTxt(timetext, TIME_TXT_FILENAME)
                        time_dict = {}
                        first_date = second_date
                        second_date = second_date+dt

            # 情绪倾向分析
            if EMOTION_ANALYSIS in mode:
                negativeemo_count = dataset[i][ARRAYID['negativeemo_count']]
                positiveemo_count = dataset[i][ARRAYID['positiveemo_count']]
                # 统计数量  {ZEROEQUNUM:0, EQUNUM:0, POSNUM:0, NEGNUM:0}
                if negativeemo_count > positiveemo_count:
                    emo_num_dict[NEGNUM] += 1
                elif negativeemo_count < positiveemo_count:
                    emo_num_dict[POSNUM] += 1
                elif negativeemo_count == positiveemo_count and positiveemo_count != 0:
                    emo_num_dict[EQUNUM] += 1
                elif negativeemo_count == positiveemo_count and positiveemo_count == 0:
                    emo_num_dict[ZEROEQUNUM] += 1

                # 统计关键词
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

            # 进度显示
            if i % 80000 == 0:
                print("\n{} / {}  ".format(i, len(dataset)), end="")
            if i % 1000 == 0:
                print("#", end="")


def mainAnalysis():
    print(" ----------- Start of data analysis ----------- ")

    # 1. 数据处理部分
    readyEnv()  # 准备环境，新建data和analysis文件夹
    excelToPickle()  # 数据转换，从excel到pkl对象化存储  目的：加速读取速度
    print('[{}] File reading in progress (6s) ...'.format(TIME()))
    dataset = readPklFile(DATA_SAVE_FILENAME)  # 此函数读取excel文件中全部数据 返回文件数据  时间大约6秒
    # print(dataset[1][21])

    # 2. 信息处理部分
    print('[{}] Keyword extraction of data ...'.format(TIME()))
    extractNKeywords(dataset)  # 提取关键词
    print('[{}] Read keyword information ...'.format(TIME()))
    nkey_array = readPklFile(ANALYSIS_NKEY_FILENAME)  # 关键词文件读取
    print(nkey_array[0], nkey_array[1])
    print('[{}] File reading completed. len_dataset:{} <-> len_nkey_array:{} ...'.format(TIME(), len(dataset), len(nkey_array)))
    if len(dataset) != len(nkey_array):
        raise Exception("数据处理出现错误，长度不一致！")
    # print('[{}] Word cloud analysis of data ...'.format(TIME()))
    # gainWordCloud(dataset)

    # 3. 分析数据
    # dataset根据时间排序
    # 1. 按时间进行关键词分析 ()
    print('[{}] Step 1: Time analysis of data ...'.format(TIME()))
    print('[{}] Step 2: Emotion analysis of data ...'.format(TIME()))
    print('[{}] Step 3: Keyword extraction and filtering ...'.format(TIME()))
    conditionAnalysis(dataset, nkey_array, [TIME_ANALYSIS, EMOTION_ANALYSIS])

    print("\n", '[{}] Keyword Time Analysis ...'.format(TIME()))
    print(INTERESTING_TEXT)

    print(" ----------- End of data analysis ----------- ")


if __name__ == '__main__':
    mainAnalysis()
