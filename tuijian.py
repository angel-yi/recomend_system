# coding:utf-8

# 思路
# 整体设计：每个部分程序分开设计
# 按照推荐位置设计不同的推荐方式
# 分类页：所有的框架分类有8个，设计一个统一模板，不论到哪一个分类都会实现
# 推荐方式：本分类下浏览量最高的10本
# 设计：1.获取分类名，2.查此分类下浏览量最高的十本，3.将此10个数据发送到分类页

# 搜索页：设计统一模板，输入任何关键词都有推荐
# 推荐方式：按照搜索词匹配浏览量最高的10本
# 设计：1。获取搜索词，2。查找搜索词对应的数据，3.将所得数据按照浏览量排序，4.截取10本发送前端

# 详情页：设计统一模板，进来一本书就按照这本书取推荐
# 推荐方式：文字匹配，相似度最高的5本
# 设计：1.将所有图书的简介进行分词，2.将所有的分词写入到static里面的fenci.csv中，
# 3.构建分词矩阵，4.获取用户所点击进来这本书的描述并进行分词，5.将描述信息放入到分词矩阵中做矩阵相乘
# 5.拿到最相似的5本返回前端，

# 个人主页：设计统一模板，不同的人推荐不同的数据（这一部分还需要再考虑，不太熟悉）
# 推荐方式：协同过滤推荐
# 设计1：获取用户的历史浏览数据，2.生成总的用户库，3.构建用户矩阵，4.得到用户画像，5.计算最相近的用户
# 6。找到最相近用户下那个用户看过的这个用户没有看的书，7.将那些书推荐给这个用户，
# 设计2：1.获取用户的历史浏览数据，2.生成总的图书库，3.构建图书矩阵，4.计算最相近的图书，5.学习网易云推荐方式
# （网易云的推荐采用用户喜欢的一首歌，推荐另一首或多首相似度较高的歌曲），根据用户看过的书使用详情页的分词库进行推荐，
# 6.将那些书推荐给这个用户，

import threading
import time

import pymysql

from mysql_connect import SqlCx
from similar import Similar
from similar_user_index import Similar as User_Sim


def FenLei(fl_name):
    """
    分类推荐函数
    :param fl_name: 分类名
    :return: 推荐列表
    """
    sql = "SELECT *,COUNT(*) AS c from history,book WHERE history.book_id=book.id " \
          "AND book_class='%s' GROUP BY book_id ORDER BY c desc LIMIT 10" % fl_name
    data = SqlCx(sql)
    tj_list = []
    if len(data) < 10:
        sx = 10 - len(data)
        if sx != 0:
            sql = "SELECT * FROM book WHERE book_class='" + fl_name + "' ORDER BY id DESC LIMIT " + str(sx)
            data_2 = SqlCx(sql)
            for i in data_2:
                if i not in data:
                    tj_list.append(i)
    try:
        data = data + tj_list
    except:
        data = tj_list
    return data


def SouSuo(ss_word):
    """
    搜索推荐函数
    :param ss_word: 搜索关键词
    :return: 推荐列表
    """
    sql = "SELECT *,COUNT(*) AS c FROM book,history WHERE book.id=history.book_id " \
          "and book_name like '%" + ss_word + "%' GROUP BY book_id ORDER BY c desc"
    data = SqlCx(sql)
    # print(data)
    tj_list_2 = []
    if len(data) < 10:
        sx = 10 - len(data)
        if sx != 0:
            sql = "SELECT * FROM book WHERE book_name like '%" + ss_word + "%' " \
                                                                           "ORDER BY id DESC LIMIT " + str(sx)
            data_2 = SqlCx(sql)
            for i in data_2:
                if i not in data:
                    tj_list_2.append(i)
    try:
        data = data + tj_list_2
    except:
        data = tj_list_2
    return data


def XqTj(book_id):
    """
    详情推荐函数
    :param book_id: 书籍id
    :return: 推荐列表
    """
    sim = Similar(book_id)
    data = sim.run()
    return data
    # hz = dict()
    # path = "abstract_recommend.csv"
    # csvfile = open(path, 'r', encoding='UTF-8')
    # reader = csv.DictReader(csvfile)
    # id = [row['id'] for row in reader]
    # csvfile = open(path, encoding='UTF-8')
    # reader = csv.DictReader(csvfile)
    # abstract = [row['tjid'] for row in reader]
    # abstract_len = len(abstract)
    # for i in range(abstract_len):
    #     hz[id[i]] = abstract[i]
    # tjid_list = str(hz['%s'%book_id]).replace("'",'').replace('[','').replace(']','').replace(' ','').split(',')
    # tjid_list.remove(str(book_id))
    # sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'"\
    #       % (tjid_list[4], tjid_list[3], tjid_list[2], tjid_list[1], tjid_list[0])
    # data = SqlCx(sql)
    # return data


# 完善

class MyThread(threading.Thread):

    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return ''


def sim(book_id, weight):
    xx = User_Sim(book_id, weight)
    xx = xx.run()
    return xx


def User_Tj(user_id):
    # 1、查找最近浏览记录
    sql = "SELECT count(*) as c FROM history WHERE user_id = '%s' GROUP BY book_id ORDER BY data desc" % user_id
    data = SqlCx(sql)
    len_data = len(data)
    if int(len_data) >= 5:
        book_id_list_2 = []
        time1 = time.time()
        sql = "SELECT book_id FROM history WHERE user_id = '%s' GROUP BY book_id ORDER BY data desc limit 10" % user_id
        data = SqlCx(sql)
        book_id_list = [i['book_id'] for i in data]
        thread_li = []
        # xx = User_Sim(book_id_list[0], 2)
        # xx = xx.run()
        # print(xx)
        # tj_id.append(xx)
        #
        # xx = User_Sim(book_id_list[1], 1)
        # xx = xx.run()
        # print(xx)
        # tj_id.append(xx)
        # xx = User_Sim(book_id_list[2], 1)
        # xx = xx.run()
        # print(xx)
        # tj_id.append(xx)
        # xx = User_Sim(book_id_list[3], 1)
        # xx = xx.run()
        # print(xx)
        # tj_id.append(xx)

        t1 = MyThread(sim, args=(book_id_list[0], 2,))
        thread_li.append(t1)
        t1.start()
        t2 = MyThread(sim, args=(book_id_list[1], 1,))
        thread_li.append(t2)
        t2.start()
        t3 = MyThread(sim, args=(book_id_list[2], 1,))
        thread_li.append(t3)
        t3.start()
        t4 = MyThread(sim, args=(book_id_list[3], 1,))
        thread_li.append(t4)
        t4.start()

        for t in thread_li:
            t.join()
            book_id_list_2.append(t.get_result())
        print(book_id_list_2)
        tj_id_str = str(book_id_list).replace('[', '').replace(']', '').replace(' ', '').replace("'", '')
        tj_id_list = tj_id_str.split(',')
        print(tj_id_list)
        time2 = time.time()
        print('时间：', time2 - time1)
        return tj_id_list
        # user_sim = User_Sim(book_id_list[0], 3).run()
        # print(user_sim)

        # 这十个数据按照一定的权重进行提取推荐数据，最近的0.3就是3本，倒数第二就是0.2两本，倒数第三就是0.2两本，其余各一本

# book_id = 2
# xq = XqTj(book_id)
# print(xq)
# 87.075679063797
# 57.69182777404785

# def read_file():
#     path = "miaoshu_fenci_50.csv"
#     hz = dict()
#     hz_2 = dict()
#     hz_3 = dict()
#     hz_4 = dict()
#     hz_5 = dict()
#     hz_6 = dict()
#     hz_7 = dict()
#     hz_8 = dict()
#     hz_9 = dict()
#     hz_10 = dict()
#     hhzz = dict()
#     csvfile = open(path, encoding='UTF-8')
#     reader = csv.DictReader(csvfile)
#     id = [row['id'] for row in reader]
#     csvfile = open(path, encoding='UTF-8')
#     reader = csv.DictReader(csvfile)
#     ms = [row['miaoshu'] for row in reader]
#     for i in range(len(ms)):
#         hhzz[id[i]] = ms[i]
#     for i in range(0, 500):
#         hz[id[i]] = ms[i]
#     for i in range(10000, 20000):
#         hz_2[id[i]] = ms[i]
#     for i in range(20000, 30000):
#         hz_3[id[i]] = ms[i]
#     for i in range(30000, 40000):
#         hz_4[id[i]] = ms[i]
#     for i in range(40000, 50000):
#         hz_5[id[i]] = ms[i]
#     for i in range(25000, 30000):
#         hz_6[id[i]] = ms[i]
#     for i in range(30000, 35000):
#         hz_7[id[i]] = ms[i]
#     for i in range(35000, 40000):
#         hz_8[id[i]] = ms[i]
#     for i in range(40000, 45000):
#         hz_9[id[i]] = ms[i]
#     for i in range(45000, 50888):
#         hz_10[id[i]] = ms[i]
#     print(len(hz))
#     return hz,hz_2,hz_3,hz_4,hz_5,hz_6,hz_7,hz_8,hz_9,hz_10, hhzz

# def TF_IDF(book_id):
#     t1 = time.time()
#     vectorizer = CountVectorizer(min_df=1, token_pattern='(?u)\\b\\w+\\b')  # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
#     transformer = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值
#     xx = read_file()[10]
#     # print(type(xx))
#     # print(len(xx))
#     b = []
#     for ms in xx.values():
#         b.append(ms)
#     # print(len(b))
#     # ff = xx['%s'%book_id]
#     # print(ff)
#     # if book_id - 1000 < 0:
#     #     aa = book_id
#     # else:
#     #     aa = book_id - 2000
#     # if book_id + 3000 > 50888:
#     #     aa = book_id - 5000
#     #     bb = book_id
#     # else:
#     #     bb = book_id + 3000
#     #
#     # print(aa, bb)
#     # print(b[50000:50002])
#     # yy = b[0:20000]
#     # for bb in b:
#
#     test = vectorizer.fit_transform(b)
#     # print('----------', test)
#     test_tfidf = transformer.fit_transform(test)  # if-idf中的输入为已经处理过的词频矩阵
#     # print(test_tfidf)
#     # print(test_tfidf.toarray())  # 输出词频矩阵的IF-IDF值
#     # print(test_tfidf.toarray().shape)
#
#     sql = "select id,book_name,book_abstract from book where id='%s'" % book_id
#     data = SqlCx(sql)
#     for data in data:
#         print(data['id'], data['book_name'])
#         input_ms = str(data['book_abstract'])[0:100]
#
#     deal_input = str(input_ms).replace('【', '').replace('】', '').replace('&nbsp;', '').replace('，', '') \
#                                                                   .replace('。', '').replace('、', '').replace('...', '').replace('？', '') \
#                                                                   .replace('！', '').replace('&amp;', '').replace('…', '').replace('”', '') \
#                                                                   .replace('“', '').replace('《', '').replace('》', '').replace('#', '') \
#                                                                   .replace('&', '').replace('；', '').replace('amp', '').replace('�', '') \
#                                                                   .replace('◆', '').replace('-', '').replace('―', '').replace('・', '') \
#                                                                   .replace('：', '').replace('［', '').replace('］', '').replace('）', '') \
#                                                                   .replace('（', '').replace('‘', '').replace('’', '')
#     input_text_jieba = jieba.cut(deal_input)
#     '''开始处理输入文本，构建对应的词频矩阵'''
#     coll = collections.Counter(input_text_jieba)
#     new_vectorizer = []
#     for word in vectorizer.get_feature_names():  # 原始词频
#         new_vectorizer.append(coll[word])  # 构建输入的全新词频
#     # ta = transformer.fit_transform(test_tfidf).toarray(dtype='float16')
#     # print(ta)
#     new_tfidf = np.array(test_tfidf.toarray(), dtype='float32').T
#     # new_tfidf.dtype('float16')
#     # print(new_tfidf)
#     print(new_tfidf.shape)
#     new_vectorizer = np.array(new_vectorizer, dtype='float32').reshape(1, len(new_vectorizer))
#     # print(new_vectorizer)
#     scores = np.dot(new_vectorizer, new_tfidf)
#     new_scores = list(scores[0])  # 将得分的一维矩阵转换为列表
#     max_location = sorted(enumerate(new_scores), key=lambda x: x[1])  # 列表坐标排序，转换为元组
#     max_location.reverse()  # 上面默认为从小到大，将他逆序
#     final_location = []
#     for i in range(3):  # 在元组中找到匹配度最高的三个数的坐标
#         print(max_location[i])
#         final_location.append(max_location[i][0])
#     for i in range(len(final_location)):
#         data_id = list(xx.keys())[list(xx.values()).index(b[final_location[i]])]
#         print(data_id)
#         sql = "select id,book_name,book_class from book where id='%s'" % data_id
#         data = SqlCx(sql)
#         print(data)
#         jieguo = b[final_location[i]]
#         # print(jieguo)
#     t2 = time.time()
#     print(t2-t1)

# jieguo = b[final_location[0]]
# print("最近匹配到的问题是：", jieguo)


# xx = FenLei('恐怖小说')
# print(xx)
# print(len(xx))
# yy = SouSuo('黑客')
# print(yy)
# print(len(yy))
# zz = Miaoshu_Fenci()
# read_file()

# book_id = 5
# TF_IDF(i=1, book_id=book_id)
# if book_id < 10000:
#     i = 0
# elif 10000 < book_id < 20000:
#     i = 1
# elif 20000 < book_id < 30000:
#     i = 2
# elif 30000 < book_id < 40000:
#     i = 3
# elif 40000 < book_id < 50888:
#     i = 4
# # print(i)
# x = threading.Thread(target=TF_IDF, args=(i, book_id,))
# x.start()
# for i in range(0,5,1):
#     print(i)
#     # if i == 0:
#     #     a = 0
#     #     b = 10000
#     # elif i == 10000:
#     #     a = 10000
#     #     b = 20000
#     # elif i == 20000:
#     #     a = 20000
#     #     b = 30000
#     # elif i == 30000:
#     #     a = 30000
#     #     b = 40000
#     # elif i == 40000:
#     #     a = 40000
#     #     b = 50888
#
#     # print(a,b)
#     x = threading.Thread(target=TF_IDF, args=(i,book_id,))
#     x.start()
# TF_IDF(10000)
# 分词句子长度50
# 矩阵大小32795*10000
# 用时23.39279270172119
