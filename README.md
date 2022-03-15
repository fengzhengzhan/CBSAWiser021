# CBSA-Data-analytic-challenge-021

# 程序说明文档

## 程序结构

程序会自动生成文件夹

- analysis  用于存放分析数据产生的中间文件
- data  用于存放原始数据



## 使用手册

1. 将文件analysis.py下载下来，首先运行一次代码，会创建两个文件data和analysis，会报错提示缺少数据文件。
2. 首先将new_analytics_challenge_dataset_edited.xlsx数据文件复制到data目录下，然后运行程序对数据文件进行转换（3分钟），要将DEBUG模式设置为False。
3. 数据转换大约需要3分钟，会在data目录下面生成一个.pkl文件，用于快速读取数据。
4. 然后程序会提取每条数据的关键词，以便后续分析。提取关键词使用的是的jieba的python库（需要提前安装），此过程需要大约2小时。
5. 如果不想等两小时，且不需要设置额外的参数，就把analysis_nkey_array.pkl拷贝到analysis文件夹下。
6. 直接运行文件就会在analysis文件夹下面生成对应的分析文件。
7. 分析文件分别是对时间的分析、对评论情绪的分析、对感兴趣内容的提取
8. 可以设置感兴趣的词语
9. 时间分析的间隔

