# coding:utf-8

import csv
import jieba
import math
import pymysql
import threading
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


class Similar():
    def __init__(self, book_id, weight):
        self.csv_path = "miaoshu_fenci_chunjing.csv"
        self.csv_to_path = "testdata.csv"
        self.hz = dict()
        self.read = self.read_file()
        self.new_abstract_dict = dict()
        self.data_dict = dict()
        self.book_id = book_id
        self.book_class = self.book_ab()[1]
        self.data_dict_two = dict()
        self.new_dict = {v: k for k, v in self.data_read_to_dict().items()}
        self.weight = weight

    def SqlCx(self, sql):
        connect = pymysql.connect(host='rm-m5e42302277dox30fno.mysql.rds.aliyuncs.com',
                                  port=3306, user='book',
                                  password='Angel_Book', db="book",
                                  cursorclass=pymysql.cursors.DictCursor)
        cursor = connect.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        # connect.close()
        connect.commit()
        return data

    def book_ab(self):
        sql = "select id, book_abstract, book_class from book where id='%s'" % self.book_id
        data = self.SqlCx(sql)
        for i in data:
            book_abs = str([x for x in jieba.cut(str(i['book_abstract']).replace('【', '').replace('】', '') \
                                                 .replace('&nbsp;', '').replace('，', '') \
                                                 .replace('。', '').replace('、', '').replace('...', '').replace('？', '') \
                                                 .replace('！', '').replace('&amp;', '').replace('…', '').replace('”',
                                                                                                                 '') \
                                                 .replace('“', '').replace('《', '').replace('》', '').replace('#', '') \
                                                 .replace('&', '').replace('；', '').replace('amp', '').replace('�', '') \
                                                 .replace('◆', '').replace('-', '').replace('―', '').replace('・', '') \
                                                 .replace('：', '').replace('［', '').replace('］', '').replace('）', '') \
                                                 .replace('（', '').replace('‘', '').replace('’', ''))]).replace('[',
                                                                                                                '').replace(
                ']', '').replace("'", '') \
                .replace(' ', '').replace(',', ' ')
            book_class = i['book_class']
        return book_abs, book_class

    def read_file(self):
        csvfile = open(self.csv_path, encoding='UTF-8')
        reader = csv.DictReader(csvfile)
        id = [row['id'] for row in reader]
        csvfile = open(self.csv_path, encoding='UTF-8')
        reader = csv.DictReader(csvfile)
        abstract = [row['abstract'] for row in reader]
        for i in range(len(abstract)):
            self.hz[id[i]] = abstract[i]
        return self.hz

    def data_read_to_dict(self):
        # 需要把数据库里的数据转换为字典形式
        sql = "select id, book_abstract from book where book_class='" + str(
            self.book_class) + "' and id!='%s'" % self.book_id
        data = self.SqlCx(sql)
        for i in data:
            self.data_dict[i['id']] = str(
                [x for x in jieba.cut(str(i['book_abstract']).replace('【', '').replace('】', '') \
                                      .replace('&nbsp;', '').replace('，', '') \
                                      .replace('。', '').replace('、', '').replace('...', '').replace('？', '') \
                                      .replace('！', '').replace('&amp;', '').replace('…', '').replace('”', '') \
                                      .replace('“', '').replace('《', '').replace('》', '').replace('#', '') \
                                      .replace('&', '').replace('；', '').replace('amp', '').replace('�', '') \
                                      .replace('◆', '').replace('-', '').replace('―', '').replace('・', '') \
                                      .replace('：', '').replace('［', '').replace('］', '').replace('）', '') \
                                      .replace('（', '').replace('‘', '').replace('’', ''))]).replace('[', '').replace(
                ']', '').replace("'", '') \
                .replace(' ', '').replace(',', ' ')
            # self.data_dict_two[str([x for x in jieba.cut(str(i['book_abstract']).replace('【', '').replace('】', '')\
            #     .replace('&nbsp;', '').replace('，', '') \
            #     .replace('。', '').replace('、', '').replace('...', '').replace('？', '') \
            #     .replace('！', '').replace('&amp;', '').replace('…', '').replace('”', '') \
            #     .replace('“', '').replace('《', '').replace('》', '').replace('#', '') \
            #     .replace('&', '').replace('；', '').replace('amp', '').replace('�', '') \
            #     .replace('◆', '').replace('-', '').replace('―', '').replace('・', '') \
            #     .replace('：', '').replace('［', '').replace('］', '').replace('）', '') \
            #     .replace('（', '').replace('‘', '').replace('’', ''))]).replace('[', '').replace(']', '').replace("'", '')\
            #     .replace(' ', '').replace(',', ' ')] = i['id']
        # print(self.data_dict)
        # 然后进行清洗和分词处理
        # 最后传递到函数里面
        return self.data_dict

    # @jit(nopython=True)
    def tf_idf(self, corpus):
        vectorizer = CountVectorizer(analyzer='word', token_pattern="(?u)\\b\\w+\\b")
        transformer = TfidfTransformer()
        tf_idf = transformer.fit_transform(vectorizer.fit_transform(corpus))
        tf_idf_finish = tf_idf.toarray()
        return tf_idf_finish

    def similarity(self, data_1, data_2):
        # print(type(data_1))
        return sum(a * b for a, b in zip(data_1, data_2)) / (math.sqrt(sum(a * b for a, b in zip(data_1, data_2)))
                                                             * math.sqrt(
                    sum(a * b for a, b in zip(data_1, data_2))) + .00000000001)

    # @jit(nopython=False)
    def recomend(self, word_1, abstract_len, word_2):
        self.sim_dict = dict()
        print('3')
        for i in range(abstract_len):
            corpus = [word_1, word_2[i]]
            # print(corpus)
            print('4')
            tf_finish = self.tf_idf(corpus)
            print('5')
            sim_sim = self.similarity(tf_finish[0], tf_finish[1])
            print('6')
            # print(sim_sim)
            self.sim_dict[sim_sim] = word_2[i]
            print('7')
        sort_sim = sorted(self.sim_dict.keys(), reverse=True)
        print('8')
        # data_id_1 = list(self.data_read_to_dict().keys())[list(self.data_read_to_dict().values()).index(word_1)]
        sim_value = [self.sim_dict[x] for x in sort_sim[0:self.weight]]
        # 所有的工作落到了这一行，怎么反求出来id，30秒就执行一句话，我笑了
        # data_id_2 = [list(self.data_read_to_dict().keys())[list(self.data_read_to_dict().values()).index(xx)] for xx in sim_value]
        # for i in sim_value:
        #     new_dict_va = new_dict[i]
        #     print(new_dict_va)
        print('9')
        data_id_2 = [self.new_dict[i] for i in sim_value]
        # sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'" \
        #       % (data_id_2[4], data_id_2[3], data_id_2[2], data_id_2[1], data_id_2[0])
        # data = self.SqlCx(sql)
        # print(data)
        return data_id_2

    def run(self):
        print("1")
        run_time_1 = time.time()
        # abstract_list_1 = [ms for ms in self.data_read_to_dict().values()]
        # print(abstract_list_1)
        abstract_list_2 = [ms for ms in self.data_read_to_dict().values()]
        print('2')
        t1 = time.time()
        data = self.recomend(self.book_ab()[0], len(abstract_list_2), abstract_list_2)
        # t2 = time.time()
        # print("单个用时：", t2-t1)
        run_time_2 = time.time()
        print("总用时：", run_time_2 - run_time_1)
        return data


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
    xx = Similar(book_id, weight)
    xx = xx.run()
    return xx


if __name__ == '__main__':
    # book_id = 1
    x = Similar(20520, 2).run()
    print(x)
    # x = Similar(100, 1).run()
    # print(x)
    # x = Similar(100, 1).run()
    # print(x)
    # x = Similar(5, 1).run()
    # print(x)

    # thread_li = []
    # book_id_list = []
    # t1 = MyThread(sim, args=(1, 2,))
    # thread_li.append(t1)
    # t1.start()
    # t2 = MyThread(sim, args=(10000, 1,))
    # thread_li.append(t2)
    # t2.start()
    # t3 = MyThread(sim, args=(10500, 1,))
    # thread_li.append(t3)
    # t3.start()
    # t4 = MyThread(sim, args=(12000, 1,))
    # thread_li.append(t4)
    # t4.start()
    # for t in thread_li:
    #     t.join()
    #     book_id_list.append(t.get_result())
    # print(book_id_list)
