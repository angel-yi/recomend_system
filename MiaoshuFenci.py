import csv
import time
import jieba

from mysql_connect import SqlCx


def Miaoshu_Fenci(book_class):
    t1 = time.time()
    sql = "SELECT id,book_abstract FROM book where book_class='%s'" % book_class
    data = SqlCx(sql)
    f = open('Fenci/{}.csv'.format(book_class), 'w', encoding='utf-8', newline='')
    csv_writer = csv.writer(f)
    csv_writer.writerow(('id', 'abstract'))
    for i in data:
        ms = str([x + '/' for x in jieba.cut(str(i['book_abstract'])
                                             .replace(r'\u3000', '').replace('vip', '').replace('~', '').replace('『',
                                                                                                                 '') \
                                             .replace('』', '').replace('*', '').replace('?', '').replace('txt', '') \
                                             .replace('【', '').replace('】', '').replace('&nbsp;', '').replace('，', '') \
                                             .replace('。', '').replace('、', '').replace('...', '').replace('？', '') \
                                             .replace('！', '').replace('&amp;', '').replace('…', '').replace('”', '') \
                                             .replace('“', '').replace('《', '').replace('》', '').replace('#', '') \
                                             .replace('&', '').replace('；', '').replace('amp', '').replace('�', '') \
                                             .replace('◆', '').replace('-', '').replace('―', '').replace('・', '') \
                                             .replace('：', '').replace('［', '').replace('］', '').replace('）', '') \
                                             .replace('（', '').replace('‘', '').replace('’', '').replace('/', '') \
                                             .replace(')', '').replace('(', '').replace('+', '').replace('.', '') \
                                             .replace('·', '').replace('—', '').replace(' ', '') \
                                             .replace('☆', '').replace('★', '').replace('＜', '').replace('～', ''),
                                             cut_all=False)]) \
            .replace('[', '').replace(']', '').replace("'", '').replace(',', '') \
            .replace(' ', '').replace('/', ' ')
        csv_writer.writerow((str(i['id']), str(ms)))
    t2 = time.time()
    print(t2 - t1)

def fenci():
    sql = "SELECT book_class FROM book group by book_class"
    data = SqlCx(sql)
    print([data['book_class'] for data in data])
    book_class_list = [data['book_class'] for data in data]
    for book_class in book_class_list:
        Miaoshu_Fenci(book_class)


if __name__ == '__main__':
    # book_class_list = ['中国文学', '互联网', '修真小说', '其他小说', '励志', '历史小说', '恐怖小说', '玄幻小说', '科幻小说', '经济学', '网游小说', '都市小说']
    # book_class = '政治学'
    fenci()
