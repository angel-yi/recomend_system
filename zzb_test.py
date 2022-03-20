# coding:utf-8
import csv
import math
import pymysql
import threading
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from MiaoshuFenci import fenci
from mysql_connect import SqlCx

stop_word_path = 'hit_stopword.txt'
stop_word_list = open(stop_word_path, 'r', encoding='utf-8').readlines()
stop_word_list = [i.replace('\n', '') for i in stop_word_list]
vectorizer = CountVectorizer(analyzer="word", stop_words=stop_word_list, tokenizer=None)
transformer = TfidfTransformer()


def read_file(book_class):
    hz = {}
    csv_path = "Fenci/{}.csv".format(book_class)
    csvfile = open(csv_path, encoding='UTF-8')
    reader = csv.DictReader(csvfile)
    id = [row['id'] for row in reader]
    csvfile = open(csv_path, encoding='UTF-8')
    reader = csv.DictReader(csvfile)
    abstract = [row['abstract'] for row in reader]
    for i in range(len(abstract)):
        hz[id[i]] = abstract[i]
    return hz


def book_ab(book_id):
    sql = "select book_class from book where id='%s'" % book_id
    data = SqlCx(sql)
    for i in data:
        book_class = i['book_class']
    # book_class_2 = data
    return book_class


def tf_idf(corpus):
    tf_idf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    tf_idf_finish = tf_idf.toarray()
    return tf_idf_finish


def similarity(data_1, data_2):
    return sum(a * b for a, b in zip(data_1, data_2)) / (math.sqrt(sum(a * b for a, b in zip(data_1, data_2)))
                                                         * math.sqrt(
                sum(a * b for a, b in zip(data_1, data_2))) + .00000000001)


def recomment(word_1, word_2, weight, x):
    sim_dict = {}
    for i in range(len(word_2)):
        corpus = [word_1, word_2[i]]
        tf_finish = tf_idf(corpus)
        # print(tf_finish)
        # print(len(tf_finish))
        sim_sim = similarity(tf_finish[0], tf_finish[1])
        # print(sim_sim)
        sim_dict[sim_sim] = word_2[i]
        print('相似度:', sim_sim)
    sort_sim = sorted(sim_dict.keys(), reverse=True)
    sim_value = [sim_dict[x] for x in sort_sim[0:weight]]
    new_dict = {v: k for k, v in x.items()}
    data_id_2 = [new_dict[i] for i in sim_value]
    return data_id_2


def run(book_id, weight, bc):
    t1 = time.time()
    print("开始执行：", book_id)
    x = read_file(bc)
    word_1 = x.pop('{}'.format(book_id))
    abstract_list_2 = [ms for ms in x.values()]
    tj_id = recomment(word_1, abstract_list_2, weight, x)
    print(book_id, '===', tj_id)
    tj_id_str = str(tj_id).replace('[', '').replace(']', '').replace("'", '')
    sql = "insert into tf values('" + str(book_id) + "', '%s')" % str(tj_id_str)
    try:
        SqlCx(sql)
    except:
        SqlCx(sql)
    t2 = time.time()
    print("用时：", t2 - t1)
    return tj_id


def driver(book_class):
    # 8个进程-16个进程/8个进程-n个多线程
    bc = book_class
    sql = "select id from book where book_class='%s'" % str(book_class)
    try:
        data = SqlCx(sql)
    except:
        data = SqlCx(sql)
    b_id = []
    for i in data:
        b_id.append(i['id'])

    cov = int(len(b_id) / 8)
    # print(cov)
    # cov_t = int(cov / 2)
    # print(cov_t)
    p_li = []
    p1 = threading.Thread(target=driver_t, args=(b_id[0:cov], bc))
    p2 = threading.Thread(target=driver_t, args=(b_id[cov:cov * 2], bc))
    p3 = threading.Thread(target=driver_t, args=(b_id[cov * 2:cov * 3], bc))
    p4 = threading.Thread(target=driver_t, args=(b_id[cov * 3:cov * 4], bc))
    p5 = threading.Thread(target=driver_t, args=(b_id[cov * 4:cov * 5], bc))
    p6 = threading.Thread(target=driver_t, args=(b_id[cov * 5:cov * 6], bc))
    p7 = threading.Thread(target=driver_t, args=(b_id[cov * 6:cov * 7], bc))
    p8 = threading.Thread(target=driver_t, args=(b_id[cov * 7:], bc))
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()
    p_li.append(p1)
    p_li.append(p2)
    p_li.append(p3)
    p_li.append(p4)
    p_li.append(p5)
    p_li.append(p6)
    p_li.append(p7)
    p_li.append(p8)
    for i in p_li:
        i.join()
    # print(len(b_id))
    # for i in b_id:
    #     # t1 = threading.Thread(target=run, args=(i, 5, bc))
    #     # t1.start()
    #     # t = multiprocessing.Process(target=run, args=(i, 5, bc, ))
    #     # t.start()
    #     try:
    #         run(i, 5, bc)
    #     except:
    #         i = i + 1
    #         run(i, 5, bc)


def driver_t(book_li, bc):
    for i in book_li:
        # try:
        run(i, 5, bc)
        # except:
        #     continue


if __name__ == '__main__':
    # "SELECT * FROM tf"
    t1 = time.time()
    sql = "select book_class from book group by book_class"
    data = SqlCx(sql)
    b_class = []
    b_id = []
    for i in data:
        b_class.append(i['book_class'])
    print(b_class)
    b_class = ['中国文学', '互联网', '励志', '历史地理', '政治与法律', '政治学', '社会科学总论', '经济', '艺术']
    sql = "TRUNCATE TABLE tf"
    t1 = time.time()
    book_class = b_class[8]
    sql = f"select id from book where book_class='{book_class}'"
    try:
        data = SqlCx(sql)
    except:
        data = SqlCx(sql)
    for i in data:
        b_id.append(i['id'])
    print(b_id)
    driver_t(b_id, book_class)
    t2 = time.time()
    print('用时:', t2 - t1)
