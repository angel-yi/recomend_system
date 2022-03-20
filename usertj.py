# coding:utf-8

import threading

from mysql_connect import SqlCx


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


def select_id(book_id, book_weight):
    sql = "select * from tf where b_id = '%s'" % str(book_id)
    data = SqlCx(sql)
    for i in data:
        data = str(i['tf']).replace(' ', '').split(',')
    return data[0:book_weight]


def User_Tj(user_id):
    """
    计算推荐书籍
    :param user_id:
    :return:
    """
    # 查找最近浏览记录
    sql = "SELECT count(*) as c FROM history WHERE user_id = '%s' GROUP BY book_id ORDER BY data desc" % user_id
    data = SqlCx(sql)
    print(len(data))
    if int(len(data)) >= 4:
        sql = "SELECT book_id FROM history WHERE user_id = '%s' GROUP BY book_id ORDER BY data desc" % user_id
        data = SqlCx(sql)
        tj_id_list = []
        tj_list = [i['book_id'] for i in data]
        print(tj_list)
        x = select_id(tj_list[0], 2)
        tj_id_list.append(str(x).replace('[', '').replace(']', '').replace("'", '').split(', '))
        tj_id_list = str(tj_id_list).replace('[', '').replace(']', '').replace("'", '').split(', ')
        for i in range(1, len(tj_list)):
            tj_list_2 = select_id(tj_list[i], 1)
            tj_list_3 = str(tj_list_2).replace('[', '').replace(']', '').replace("'", '')
            if tj_list_3 not in tj_id_list and tj_list_3 != '()':
                tj_id_list.append(tj_list_3)
            else:
                i += 1
        print(tj_id_list)
        data = str(tj_id_list).replace('[', '').replace(']', '').replace("'", '').split(', ')
        sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'" \
              % (data[4], data[3], data[2], data[1], data[0])
        data = SqlCx(sql)
        print(data)
        return data
    else:
        a = 5 - len(data)
        tj_id_list = []
        sql = "SELECT book_id FROM history WHERE user_id = '%s'" % user_id + " GROUP BY book_id ORDER BY data desc"
        data = SqlCx(sql)
        tj_list = [i['book_id'] for i in data]
        try:
            for i in tj_list:
                if i == 0:
                    x = select_id(i, 2)
                    tj_id_list.append(x)
                else:
                    x = select_id(i, 1)
                    tj_id_list.append(x)
            sql = "SELECT COUNT(history.id) AS count, book_id FROM history,book WHERE book.id=history.book_id  GROUP BY book_id ORDER BY COUNT(history.id) DESC LIMIT %s" % a
            x_3 = SqlCx(sql)
            x_3 = [i['book_id'] for i in x_3]
            tj_id_list.append(x_3)
            data = str(tj_id_list).replace('[', '').replace(']', '').replace("'", '').split(', ')
            sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'" \
                  % (data[4], data[3], data[2], data[1], data[0])
            data = SqlCx(sql)
            print(data)
            return data
        except:
            sql = "SELECT COUNT(history.id) AS count, book_id FROM history,book WHERE book.id=history.book_id  GROUP BY book_id ORDER BY COUNT(history.id) DESC LIMIT %s" % a
            x_3 = SqlCx(sql)
            x_3 = [i['book_id'] for i in x_3]
            tj_id_list.append(x_3)
            data = str(tj_id_list).replace('[', '').replace(']', '').replace("'", '').split(', ')
            sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'" \
                  % (data[4], data[3], data[2], data[1], data[0])
            data = SqlCx(sql)
            print(data)
            return data


def same_data(list):
    print("开始检查列表")
    for x in list:
        for y in list:
            if x == y:
                print("出现重复值", x, y)
            else:
                print("正常执行")


def history_read(user_id):
    """
    用户历史阅读记录推荐书本计算
    :param user_id:
    :return:
    """
    sql = "SELECT book_id FROM yuedu_history WHERE user_id = %s order BY data DESC" % user_id
    data = SqlCx(sql)
    book_id = [i['book_id'] for i in data]
    if int(len(book_id)) >= 3:
        sql = "SELECT book_id FROM yuedu_history WHERE user_id = %s order BY data DESC limit 3" % user_id
        data = SqlCx(sql)
        tj_id_list = []
        tj_list = [i['book_id'] for i in data]
        x = select_id(tj_list[0], 3)
        tj_id_list.append(x)
        x_2 = select_id(tj_list[1], 1)
        tj_id_list.append(x_2)
        x_3 = select_id(tj_list[2], 1)
        tj_id_list.append(x_3)
        data = str(tj_id_list).replace('[', '').replace(']', '').replace("'", '').split(', ')
        return data
    else:
        a = 5 - len(book_id)
        tj_id_list = []
        sql = "SELECT book_id FROM yuedu_history WHERE user_id = '%s'" % user_id + " GROUP BY book_id ORDER BY data desc"
        data = SqlCx(sql)
        tj_list = [i['book_id'] for i in data]
        try:
            for i in tj_list:
                if i == 0:
                    x = select_id(i, 2)
                    tj_id_list.append(x)
                else:
                    x = select_id(i, 1)
                    tj_id_list.append(x)
            sql = "SELECT COUNT(history.id) AS count, book_id FROM history,book WHERE book.id=history.book_id  GROUP BY book_id ORDER BY COUNT(history.id) DESC LIMIT %s" % a
            x_3 = SqlCx(sql)
            x_3 = [i['book_id'] for i in x_3]
            tj_id_list.append(x_3)
            data = str(tj_id_list).replace('[', '').replace(']', '').replace("'", '').split(', ')
            return data
        except:
            sql = "SELECT COUNT(history.id) AS count, book_id FROM history,book WHERE book.id=history.book_id  GROUP BY book_id ORDER BY COUNT(history.id) DESC LIMIT %s" % a
            x_3 = SqlCx(sql)
            x_3 = [i['book_id'] for i in x_3]
            tj_id_list.append(x_3)
            data = str(tj_id_list).replace('[', '').replace(']', '').replace("'", '').split(', ')
            return data


if __name__ == '__main__':
    # User_Tj(16)
    history_read(16)
