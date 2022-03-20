# coding: utf-8
import pymysql

def SqlCx(sql):
    """
    数据库查询函数, 此处用于连接数据库，务必要修改
    :param sql: SQL语句
    :return:
    """
    # 数据库一，阿里云数据库
    connect = pymysql.connect(host='rm-m5e42302277dox30fno.mysql.rds.aliyuncs.com',
                              port=3306, user='book',
                              password='Angel_Book', db="book",
                              cursorclass=pymysql.cursors.DictCursor)
    # 数据库二，本地数据库
    # connect = pymysql.connect(host='localhost',
    #                           port=3306, user='root',
    #                           password='1234', db="book",
    #                           cursorclass=pymysql.cursors.DictCursor)
    cursor = connect.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    # 这句话加上会导致无法更新数据
    # connect.close()
    connect.commit()
    return data