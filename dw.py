# coding: utf-8
import datetime
import os
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie

from mysql_connect import SqlCx


def info_count():
    sql = f"select data from history order by data asc"
    data = SqlCx(sql)
    # 折线图 分类 统计
    detail_date_list = []
    data_dict = {}
    for i in data:
        a = i['data']
        b = datetime.datetime.strftime(a, '%y-%m-%d')
        print(b)
        detail_date_list.append(str(b))
    for key in detail_date_list:
        data_dict[key] = data_dict.get(key, 0) + 1
    bar = Bar()
    # 指定柱状图的横坐标
    bar.add_xaxis(list(data_dict.keys()))
    # 指定柱状图的纵坐标，而且可以指定多个纵坐标
    bar.add_yaxis("每日浏览量", list(data_dict.values()))
    # 指定柱状图的标题
    bar.set_global_opts(title_opts=opts.TitleOpts(title="每日浏览量统计图"))
    # 参数指定生成的html名称
    path = 'templates/1.html'
    try:
        os.remove(path)
    except:
        print()
    bar.render(path)

def user_count():
    sql = f"select user_reg_date from users_data order by user_reg_date asc"
    data = SqlCx(sql)
    # print(data)
    # 折线图 分类 统计
    detail_date_list = []
    data_dict = {}
    for i in data:
        a = i['user_reg_date']
        b = datetime.datetime.strftime(a, '%y-%m-%d')
        detail_date_list.append(str(b))
    for key in detail_date_list:
        data_dict[key] = data_dict.get(key, 0) + 1
    bar = Bar()
    # 指定柱状图的横坐标
    bar.add_xaxis(list(data_dict.keys()))
    # 指定柱状图的纵坐标，而且可以指定多个纵坐标
    bar.add_yaxis("数量统计", list(data_dict.values()))
    # 指定柱状图的标题
    bar.set_global_opts(title_opts=opts.TitleOpts(title="用户注册数量统计图"))
    # 参数指定生成的html名称
    path = 'templates/2.html'
    try:
        os.remove(path)
    except:
        print()
    bar.render(path)

def class_count():
    sql = f"SELECT book_class,COUNT(*) as c FROM book GROUP BY book_class"
    data = SqlCx(sql)
    detail_date_list = []
    data_dict = {}
    book_class_list = [i['book_class'] for i in data]
    book_class_count_list = [i['c'] for i in data]
    print(book_class_list)
    print(book_class_count_list)
    data_pair = [list(z) for z in zip(book_class_list, book_class_count_list)]
    pie = (Pie()
    #        .add(
    #     "",
    #     data_pair=data_pair,
    #     radius=["30%", "75%"],
    #     center=["25%", "50%"],
    #     rosetype="radius",
    #     label_opts=opts.LabelOpts(is_show=False),
    # )
           .add(
        "",
        data_pair=data_pair,
        radius=["30%", "75%"],
        center=["50%", "50%"],
        rosetype="area",
    )
           .set_global_opts(title_opts=opts.TitleOpts())
           )
    # 指定柱状图的标题
    # pie.set_global_opts(title_opts=opts.TitleOpts(title="每日浏览量统计图"))
    # 参数指定生成的html名称
    path = 'templates/3.html'
    try:
        os.remove(path)
    except:
        print()
    pie.render(path)