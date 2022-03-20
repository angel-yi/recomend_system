# coding:utf-8
import datetime
import multiprocessing
import os
import random
import time
from datetime import timedelta
import requests
import upyun

from tuijian import FenLei, SouSuo
from zzb_test import run as Run
from MiaoshuFenci import Miaoshu_Fenci
from usertj import User_Tj as usertj, history_read
import pymysql
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, session, request, flash, redirect, url_for

import dw
from mysql_connect import SqlCx
from sqlalchemy_packeg import *

pymysql.install_as_MySQLdb()

app = Flask(__name__)

# 数据库配置类
class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql://book:Angel_Book@rm-m5e42302277dox30fno.mysql.rds.aliyuncs.com:3306/book"
    # SQLALCHEMY_DATABASE_URI = "mysql://root:1234@localhost:3306/book"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'bvksdcjavcvavskbaleb'
    # SQLALCHEMY_ECHO = True
    # SQLALCHEMY_POOL_SIZE = 100000
    # SQLALCHEMY_POOL_TIMEOUT = 30
    # SQLALCHEMY_MAX_OVERFLOW = 100000
    # SESSION过期时间设置
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)

# 配置信息，初始化相关对象
app.config.from_object(Config)
bootstrap = Bootstrap()
moment = Moment()
bootstrap.init_app(app)
moment.init_app(app)
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static\\book_img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'])
image_ext = ['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF']

def safe():
    """
    安全管理函数，处于登录状态返回请求页面，非登录状态返回登录页面
    :return: 登录函数
    """
    if session.get('user_id') == '':
        return redirect(url_for("login"))

@app.route("/login", methods=["POST", "GET"])
def login():
    """
    登录
    :return:
    """
    if request.method == 'POST':
        account = request.form.get('account')
        password = request.form.get('pwd')
        user = Users.query.filter(Users.account == account, Users.password == password).first()
        if user:
            sql = "select is_administrator from user where account=%s" % account
            if SqlCx(sql)[0]['is_administrator'] == 1:
                username = Users.query.filter(Users.account == account, Users.password == password).first()
                session['account'] = account
                session['password'] = password
                session['username'] = username.username
                session['user_id'] = username.id
                session['admin_user'] = account
                print('管理员登录--', username.username)
                return redirect(url_for("background_system"))
            else:
                username = Users.query.filter(Users.account == account, Users.password == password).first()
                session['account'] = account
                session['password'] = password
                session['username'] = username.username
                session['user_id'] = username.id
                print('用户登录--', username.username)
                # 延长保存时间
                # session.permanent = True
                # 账号密码正确，重定向到首页
                # import smtplib
                # from email.mime.text import MIMEText
                # subject = "用户登录"
                # sender = "18893465250@163.com"
                # content = "sir,用户昵称为%s的用户登录了！"%username.username
                # recver = "2591301338@qq.com"
                # password = "siyi4141"
                # message = MIMEText(content, "plain", "utf-8")
                # # content 发送内容     "plain"文本格式   utf-8 编码格式
                # message['Subject'] = subject
                # message['To'] = recver
                # message['From'] = sender
                # smtp = smtplib.SMTP_SSL("smtp.163.com", 465)
                # smtp.login(sender, password)
                # smtp.sendmail(sender, [recver], message.as_string())
                # smtp.close()
                response = redirect(url_for("index"))
                response.set_cookie('username', username.username, max_age=7 * 24 * 3600)
                return response
        else:
            flash("账号或密码不正确！")
    else:
        return render_template("login.html")
    return render_template("login.html")

@app.route("/background/management/system", methods=["POST", "GET"])
def background_system():
    admin_user = session.get('admin_user')
    print(admin_user)
    if admin_user:
        return render_template("background_system.html")
    else:
        return redirect(url_for('login'))

@app.route("/class_system", methods=["POST", "GET"])
@app.route("/class_system/<int:page>", methods=["POST", "GET"])
def class_system(page=1):
    if session.get('admin_user'):
        sql = "select book_class,COUNT(*) AS c from book group by book_class"
        book_class = SqlCx(sql)
        page_num = len(book_class) / 5
        book_class = book_class[(page - 1) * 5:(page * 5)]
        return render_template("class_system.html", book_class=book_class, page=page, page_num=int(page_num))
    else:
        return redirect(url_for('login'))

@app.route('/edit_class', methods=['POST'])
def admin_edit_class():
    if session.get('admin_user'):
        if request.method == 'POST':
            old_book_class = request.form.get('old_book_class')
            new_book_class = request.form.get('new_book_class')
            sql = f"update book set book_class='{new_book_class}' where book_class='{old_book_class}'"
            SqlCx(sql)
        return redirect(url_for('class_system'))
    else:
        return redirect(url_for('login'))

@app.route("/book_system", methods=["POST", "GET"])
@app.route("/book_system/<int:page>", methods=["POST", "GET"])
def book_system(page=1):
    if session.get('admin_user'):
        sql = "select * from book"
        book_class = SqlCx(sql)
        page_num = len(book_class) / 5
        book_class = book_class[(page - 1) * 5:(page * 5)]
        return render_template("book_system.html", book_class=book_class, page=page, page_num=int(page_num))
    else:
        return redirect(url_for('login'))

@app.route("/background_author_system", methods=["POST", "GET"])
def background_author_system():
    if session.get('admin_user'):
        sql = "select * from user where user.isauthor=1"
        author = SqlCx(sql)
        return render_template("author_system.html", author=author)
    else:
        return redirect(url_for('login'))

@app.route("/member_system", methods=["POST", "GET"])
def member_system():
    if session.get('admin_user'):
        sql = "SELECT *,user.username,COUNT(*) AS c from user,history where user.is_member=1 AND user.id=history.user_id GROUP BY user.username"
        member = SqlCx(sql)
        return render_template("member_system.html", member=member)
    else:
        return redirect(url_for('login'))

@app.route("/publicity_system", methods=["POST", "GET"])
def publicity_system():
    if session.get('admin_user'):
        sql = "SELECT * from publicity"
        publicity = SqlCx(sql)
        return render_template("publicity_system.html", publicity=publicity)
    else:
        return redirect(url_for('login'))

@app.route("/send_publicity", methods=["POST"])
def send_publicity():
    if session.get('admin_user'):
        if request.method == 'POST':
            title = request.form.get('title')
            name = request.form.get('administrator_name')
            content = request.form.get('content')
            da = datetime.datetime.now()
            sql = f"insert into publicity value (null ,'{title}', '{name}', '{da}', '{content}')"
            SqlCx(sql)
            return redirect(url_for('publicity_system'))
    else:
        return redirect(url_for('login'))

@app.route("/delete_publicity", methods=["POST"])
def delete_publicity():
    if session.get('admin_user'):
        if request.method == 'POST':
            publicity_id = request.form.get('publicity_id')
            sql = f"delete from publicity where id='{publicity_id}'"
            SqlCx(sql)
            return redirect(url_for('publicity_system'))
    else:
        return redirect(url_for('login'))

@app.route("/data_system", methods=["GET"])
def data_system():
    if session.get('admin_user'):
        return render_template('data_system.html')
    else:
        return redirect(url_for('login'))

@app.route('/data/<int:name>', methods=['GET'])
def admin_system_data_profile(name):
    # dw.info_count()
    # dw.user_count()
    dw.class_count()
    return render_template(f'{name}.html')

@app.route("/xiugaixinxi", methods=['POST', 'GET'])
def xiugaixinxi():
    """
    修改个人信息
    :return:
    """

    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    user_id = session.get('user_id')
    if request.method == 'POST':
        username = request.form.get('username')
        account = request.form.get('account')
        password = request.form.get('pwd1')
        password2 = request.form.get('pwd2')
        like = request.form.get('selest')
        # Users.query.filter(Users.account == account, Users.password == password).first()
        user = Users.query.filter(Users.account == account).first()
        # print(user.password)
        if password != user.password:
            flash("与原密码不一致")
        elif len(password2) > 8:
            flash("密码太长")
        elif len(str(username)) > 10:
            flash("昵称过长")
        elif str(account).isdigit():
            Users.query.filter(Users.account == account).update({'username': '%s' % username,
                                                                 'password': '%s' % password2,
                                                                 'perference': '%s' % like})
            db.session.commit()
            db.session.close()
            session.clear()
            session['account'] = account
            session['password'] = password2
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for("login"))
        else:
            flash("账号由纯数字组成")
    return render_template("xiugaixinxi.html", publicity=publicity)


@app.route("/mycollection")
def mycollection():
    """
    我的收藏
    :return:
    """

    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    user_id = session.get('user_id')
    sql = "SELECT * FROM book,collection WHERE book.id=collection.book_id AND collection.user_id='%s' order by collection.id desc" % user_id
    mycollection = SqlCx(sql)
    return render_template("mycollection.html", collection=mycollection, publicity=publicity)


@app.route("/myhistory")
def myhistory():
    """
    历史记录
    :return:
    """

    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    user_id = session.get('user_id')
    sql = "SELECT * FROM yuedu_history,book where book.id=yuedu_history.book_id and user_id='%s'  ORDER BY url DESC" % user_id
    myhistory = SqlCx(sql)
    return render_template("myhistory.html", history=myhistory, publicity=publicity)


@app.route("/shoucang/<int:book_id>")
def collection(book_id):
    """
    收藏操作
    :param book_id: 书本id
    :return:
    """

    username = session.get('username')
    user_id = session.get('user_id')
    print('收藏--', username, '-----', book_id)
    try:
        da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        collection = Collection.query.filter(Collection.user_id == user_id, Collection.book_id == book_id).first()
        if collection:
            flash("您已收藏过本书")
        else:
            new_collection = Collection(user_id=int(user_id), book_id=int(book_id), id=None, data=da)
            db.session.add(new_collection)
            db.session.commit()
            sql = "select id from book_count where book_id=%s" % book_id
            d = SqlCx(sql)
            if d:
                print("data存在")
                sql = "update book_count set book_collection=book_collection+1 where book_id=%s" % book_id
                SqlCx(sql)
            else:
                print("data不存在")
                sql = "insert into book_count values(null,'" + book_id + "',0,1,0,0)"
                SqlCx(sql)
            return redirect(url_for("xiangqing", book_id=book_id))
    except:
        return render_template("loginerror.html")
    return redirect(url_for("xiangqing", book_id=book_id))


@app.route("/like/<int:book_id>")
def like(book_id):
    """
    点赞操作
    :param book_id:
    :return:
    """

    username = session.get('username')
    user_id = session.get('user_id')
    print('点赞--', username, '-----', book_id)
    try:
        da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        like = Like.query.filter(Like.user_id == user_id, Like.book_id == book_id).first()
        if like:
            flash("您已点赞过本书")
        else:
            new_like = Like(user_id=int(user_id), book_id=int(book_id), id=None, data=da)
            db.session.add(new_like)
            db.session.commit()
            sql = "select id from book_count where book_id=%s" % book_id
            d = SqlCx(sql)
            if d:
                print("data存在")
                sql = "update book_count set book_like=book_like+1 where book_id=%s" % book_id
                SqlCx(sql)
            else:
                print("data不存在")
                sql = "insert into book_count values(null,'" + book_id + "',0,0,1,0)"
                SqlCx(sql)
            return redirect(url_for("xiangqing", book_id=book_id))
    except:
        return render_template("loginerror.html")
    return redirect(url_for("xiangqing", book_id=book_id))



@app.route("/userinfo")
def userinfo():
    """
    用户主页，包含用户最近浏览推荐操作函数
    :return:
    """
    # 最近浏览推荐
    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    user_id = session.get('user_id')
    data = usertj(user_id)
    print(data)
    print(len(data))
    # sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'" \
    #       % (data[4], data[3], data[2], data[1], data[0])
    # data = SqlCx(sql)
    data_2 = history_read(user_id)
    sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'" \
          % (data_2[4], data_2[3], data_2[2], data_2[1], data_2[0])
    data_2 = SqlCx(sql)
    sql = "select count(*) as c from history where user_id=%s" % user_id
    mypoint = SqlCx(sql)
    sql = "select * from user where id=%s" % user_id
    info = SqlCx(sql)
    return render_template("userinfo.html", zuijin=data, lishi=data_2, mypoint=mypoint, info=info, publicity=publicity)


@app.route("/author_system")
def author_system():
    """
    作者系统
    :return:
    """

    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    # 检测是否是在登录状态，如果未登录，则返回登录，如果已登录，直接进入后台
    user_id = session.get('user_id')
    data = usertj(user_id)
    sql = "select count(*) as c from history where user_id=%s" % user_id
    mypoint = SqlCx(sql)
    sql = "select * from user where id=%s" % user_id
    info = SqlCx(sql)
    # code = [i for i in random.randint(0,9)]
    code = 2525
    return render_template("author.html", mypoint=mypoint, info=info, code=code, publicity=publicity)


def jieba_save(book_class):
    p2 = multiprocessing.Process(target=Miaoshu_Fenci, args=(book_class,))
    p2.start()
    p2.join()


def tf_cos(book_id, book_class):
    p1 = multiprocessing.Process(target=Run, args=(book_id, 5, book_class))
    p1.start()


def allowed_file(filename):
    """
    上传文件验证操作
    :param filename: 图片名称
    :return:
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/create_book", methods=["POST", "GET"])
def create_book():
    """
    新建图书
    :return:
    """

    if request.method == "GET":
        publicity = "select * from publicity order by publicity.date desc"
        publicity = SqlCx(publicity)
        sql = "select book_class from book group by book_class"
        data = SqlCx(sql)
        return render_template("create_book.html", data=data, publicity=publicity)
    elif request.method == "POST":
        # 获取前端数据
        file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
        book_name = request.form.get("book_name")
        book_author = request.form.get("book_author")
        book_abstract = request.form.get("book_abstract")
        book_class = request.form.get("book_class")
        book_img_link = request.form.get("book_img_link")
        book_img = request.files.get('book_img')
        if "image" in str(book_img):
            if book_img and allowed_file(book_img.filename) and book_img_link == '':
                now_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前时间
                file_ext = str(book_img.filename).split('.', 1)[-1]
                ranint = ''.join(str(random.choice(range(10))) for _ in range(2))
                ranint_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                new_book_id = ranint_time + ranint
                book_img_path = "/static/book_img/" + str(new_book_id) + '.' + file_ext
                new_book_img_name = str(new_book_id) + '.' + file_ext
                book_img.save(os.path.join(file_dir, new_book_img_name))
                sql = "insert into book values('" + new_book_id + "','" + str(book_name) + "','" + str(
                    book_author) + "','" + \
                      str(book_abstract) + "','" + str(book_class) + "','" + str(book_img_path) + "',null,null)"
                SqlCx(sql)
                user_id = session.get('user_id')
                da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                sql = "insert into book_author values(null,'" + str(new_book_id) + "','" + str(user_id) + "','" + str(
                    da) + "')"
                SqlCx(sql)
                sql = "insert into book_count values(null,'" + str(new_book_id) + "',0,0,0,0)"
                SqlCx(sql)
                jieba_save(book_class)
                tf_cos(new_book_id, book_class)
                return redirect(url_for("my_book"))
            if book_img_link:
                flash("上传图片和输入图片链接只可选择一种操作")
            else:
                flash("图片格式有误，只支持后缀为png,jpg,gif,JPG,PNG,GIF")
        else:
            book_img_link_ext = str(book_img_link).split('.', 3)[-1]
            if book_img_link_ext in image_ext:
                req = requests.get(book_img_link)
                if req.status_code == 200:
                    ranint = ''.join(str(random.choice(range(10))) for _ in range(2))
                    ranint_time = datetime.datetime.now().strftime("%d%H%M%S")
                    new_book_id = ranint_time + ranint
                    sql = "insert into book values(" + new_book_id + ",'" + str(book_name) + "','" + str(
                        book_author) + "','" + \
                          str(book_abstract) + "','" + str(book_class) + "','" + str(book_img_link) + "',null,null)"
                    SqlCx(sql)
                    user_id = session.get('user_id')
                    da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    sql = "insert into book_author values(null,'" + str(new_book_id) + "','" + str(
                        user_id) + "','" + str(da) + "')"
                    SqlCx(sql)
                    sql = "insert into book_count values(null,'" + str(new_book_id) + "',0,0,0,0)"
                    SqlCx(sql)
                    jieba_save(book_class)
                    tf_cos(new_book_id, book_class)
                    return redirect(url_for("my_book"))
                else:
                    flash("图片无法访问，请检查图片链接")
            else:
                flash("图片格式有误，只支持后缀为png,jpg,gif,JPG,PNG,GIF")

        return render_template("create_book.html")
    return render_template("create_book.html")


@app.route("/delete_my_book", methods=["POST", "GET"])
def delete_my_book():
    """
    删除图书
    :return:
    """

    book_id = request.form.get("book_id")
    # 获取前端传来的book_id
    safe_code = safe()
    if safe_code == 1:
        user_id = session.get("user_id")
        sql = "delete from book where id=%s" % book_id
        SqlCx(sql)
        sql = "delete from book_author where book_id=%s" % book_id
        SqlCx(sql)
        sql = "delete from book_count where id=%s" % book_id
        SqlCx(sql)
        sql = "delete from collection where book_id=%s" % book_id
        SqlCx(sql)
        sql = "delete from comment where book_id=%s" % book_id
        SqlCx(sql)
        sql = "delete from history where book_id=%s" % book_id
        SqlCx(sql)
        # sql = "delete from like where book_id=%s" % book_id
        # SqlCx(sql)
        sql = "delete from tf where b_id=%s" % book_id
        SqlCx(sql)
        sql = "delete from yuedu_history where book_id=%s" % book_id
        SqlCx(sql)
        da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        sql = "insert into author_delete_book values(null,'" + str(user_id) + "','" + str(book_id) + "','" + da + "')"
        SqlCx(sql)
    else:
        return redirect(url_for("login"))
    return redirect(url_for("my_book"))


@app.route("/my_book")
def my_book():
    """
    我的作品
    :return:
    """

    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    user_id = session.get("user_id")
    if user_id:
        # "SELECT * FROM book WHERE book_author='司毅'"
        sql = "select * from book,book_author,book_count WHERE book.id=book_author.book_id" \
              " AND book.id=book_count.book_id and book_author.user_id=%s order by book_author.date desc" % user_id
        data = SqlCx(sql)
        return render_template("my_book.html", data=data, publicity=publicity)
    else:
        return redirect(url_for("login"))
    return render_template("my_book.html")


@app.route("/edit_my_book", methods=["POST"])
def edit_my_book():
    """
    编辑文章
    :return:
    """

    book_id = request.form.get("book_id")
    book_name = request.form.get("book_name")
    book_title = request.form.get("book_title")
    book_content = request.form.get("book_content")
    book_title_content = book_title + "biaotineirong" + book_content + "     "
    with open("static/book/{}.txt".format(book_name), 'w', encoding='utf-8') as f:
        f.write(book_title_content)
        f.close()
    return redirect(url_for("yuedu", book_id=book_id))


@app.route("/certification", methods=["POST", "GET"])
def certification():
    """
    作者身份认证1
    :return:
    """

    if request.method == "GET":
        publicity = "select * from publicity order by publicity.date desc"
        publicity = SqlCx(publicity)
        user_id = session.get('user_id')
        data = usertj(user_id)
        sql = "select count(*) as c from history where user_id=%s" % user_id
        mypoint = SqlCx(sql)
        sql = "select * from user where id=%s" % user_id
        info = SqlCx(sql)
        # code = [i for i in random.randint(0,9)]
        code = 4589
        return render_template("certification.html", mypoint=mypoint, info=info, code=code, publicity=publicity)


@app.route("/certificate", methods=["POST"])
@app.route("/certificate/<cer_code>", methods=["GET"])
def certificate(cer_code=0):
    """
    作者身份认证2
    :param cer_code:
    :return:
    """

    if request.method == "POST":
        account = request.form.get('account')
        realname = request.form.get('realname')
        tel = request.form.get('tel')
        email = request.form.get('email')
        code = request.form.get('code')
        code_2 = request.form.get('code_2')
        print(code)
        print(code_2)
        if code != code_2:
            flash("验证码输入错误")
        elif len(tel) != 11:
            flash("手机号码格式错误")
        else:
            # md5加密
            import hashlib
            m = hashlib.md5()
            m.update(realname.encode(encoding='utf-8'))
            md5_code = m.hexdigest()
            hash_name = hash(realname)
            print(hash_name)
            # 信息存入数据库
            sql = "update user set realname='%s', tel='%s', email='%s', code='%s' where account=%s" % (str(realname),
                                                                                                       str(tel),
                                                                                                       str(email),
                                                                                                       str(md5_code),
                                                                                                       account)
            SqlCx(sql)
            # 发送认证邮件
            import smtplib
            from email.mime.text import MIMEText
            subject = "作者验证"
            sender = "18893465250@163.com"
            password = "siyi4141"
            content = realname + "我们已收到您的认证申请，请您点击下面的链接完成认证！" \
                                 "http://localhost:5000/certificate/%s" % md5_code
            message = MIMEText(content, "plain", "utf-8")
            message['Subject'] = subject
            message['To'] = email
            message['From'] = sender
            smtp = smtplib.SMTP_SSL("smtp.163.com", 465)
            smtp.login(sender, password)
            smtp.sendmail(sender, [email], message.as_string())
            smtp.close()
            user_id = session.get('user_id')
            data = usertj(user_id)
            sql = "select count(*) as c from history where user_id=%s" % user_id
            mypoint = SqlCx(sql)
            sql = "select * from user where id=%s" % user_id
            info = SqlCx(sql)
            # code = [i for i in random.randint(0,9)]
            code = 1234
            return "验证邮件已发送，请您注意查收！"
    elif request.method == "GET":
        return "认证申请已发送至后台管理员，待审核后就成为天使之梦小说网的认证作者啦，审核时间为1~3个工作日，请耐心等待"
    user_id = session.get('user_id')
    data = usertj(user_id)
    sql = "select count(*) as c from history where user_id=%s" % user_id
    mypoint = SqlCx(sql)
    sql = "select * from user where id=%s" % user_id
    info = SqlCx(sql)
    # code = [i for i in random.randint(0,9)]
    code = 4598
    return render_template("certification.html", mypoint=mypoint, info=info, code=code)


@app.route("/yuedu/<book_id>/<int:page>")
@app.route("/yuedu/<book_id>")
def yuedu(book_id, page=0):
    """
    阅读页
    :param book_id:
    :param page:
    :return:
    """
    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    sql = "select book_name from book where id = %s" % book_id
    data = SqlCx(sql)
    book_name = str([i['book_name'] for i in data]).replace('[', '').replace(']', '').replace("'", '')
    username = session.get('username')
    user_id = session.get('user_id')
    print('正在阅读---', username, '-----', book_name, '----', page)
    url = '/yuedu/' + str(book_name) + '/' + str(page)
    da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        sql = "delete from yuedu_history where book_name='%s' and user_id='%s'" % (book_name, user_id)
        SqlCx(sql)
    except Exception as e:
        print(e)
    try:
        # new_history = Yueduhistory(user_id=int(user_id), url=str(url), id=None, data=da, book_id=book_id, book_name=str(book_name))
        # db.session.add(new_history)
        # db.session.commit()
        sql = "insert into yuedu_history values(null,%s,'%s',%s,'%s','%s')" % (book_id, book_name, user_id, url, da)
        SqlCx(sql)
    except Exception as e:
        print('未登录用户正在阅读---', book_name, '---', page, e)
    try:
        up = upyun.UpYun('angel-xiaoshuo', 'angel0041', 'ElilaZy2B8IbvGD7v4Jq4Rv4gAag8uj1', timeout=30,
                         endpoint=upyun.ED_AUTO)
        x = up.get('/txt/%s.txt' % book_name)
        zj = x.split('     ')
        zjj = zj[page]
        if len(zjj) > 60:
            return render_template("yuedu.html", x=zj[page].split('biaotineirong'), book_id=book_id, page=page,
                                   page_num=len(zj), publicity=publicity)
        else:
            return render_template("yuedu.html", x=zj[page + 1].split('biaotineirong'), book_id=book_id,
                                   page=page + 1, page_num=len(zj), publicity=publicity)

    except Exception as e:
        print(e)
        try:
            x = open('static/book/%s.txt' % book_name, 'r', encoding='utf-8')
            x = x.read()
            # print(x)
            zj = x.split('     ')
            zjj = zj[page]
            if len(zjj) > 60:
                return render_template("yuedu.html", x=zj[page].split('biaotineirong'), book_id=book_id, page=page,
                                       page_num=len(zj))
            else:
                return render_template("yuedu.html", x=zj[page + 1].split('biaotineirong'), book_id=book_id,
                                       page=page + 1,
                                       page_num=len(zj), publicity=publicity)
        except:

            book = Book.query.filter(Book.book_name == book_name).first()
            # print(book.id)
            return render_template("yueduerror.html", x=book.book_link, book_name=book_name, publicity=publicity)


@app.route('/')
@app.route('/index')
def index():
    """
    首页
    :return:
    """
    # username = request.cookies.get('username', '')
    # print('用户进入---', session.get('username'))
    # xiaoshuo = Book.query.filter_by(book_class="励志")
    # zuire = Book.query.filter_by(book_class="中国文学")
    # manhua = Book.query.filter_by(book_class="互联网")
    # qingchunwenxue = Book.query.filter_by(book_class="历史小说")
    # aiqing = Book.query.filter_by(book_class="网游小说")

    qingchunwenxue = "select * from book where book.book_class='政治与法律'"
    manhua = "select * from book where book.book_class='互联网'"
    zuire = "select * from book where book.book_class='中国文学'"
    xiaoshuo = "select * from book where book.book_class='励志'"
    aiqing = "select * from book where book.book_class='社会科学总论'"
    qingchunwenxue = SqlCx(qingchunwenxue)
    manhua = SqlCx(manhua)
    zuire = SqlCx(zuire)
    xiaoshuo = SqlCx(xiaoshuo)
    aiqing = SqlCx(aiqing)
    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    sql = "SELECT COUNT(history.id) AS count, book_id, book_name FROM history,book WHERE book.id=history.book_id  GROUP BY book_id ORDER BY COUNT(history.id) DESC LIMIT 10"
    book_paihang = SqlCx(sql)
    sql = "SELECT COUNT(history.id) AS count, user_id, username FROM history,user WHERE user.id=history.user_id  GROUP BY user_id ORDER BY COUNT(history.id) DESC LIMIT 10"
    user_paihang = SqlCx(sql)
    return render_template("index.html", xiaoshuo=xiaoshuo[0:10], zuire=zuire[0:10], manhua=manhua[0:10],
                           qingchunwenxue=qingchunwenxue[0:10],
                           aiqing=aiqing[0:10], book_paihang=book_paihang, user_paihang=user_paihang,
                           publicity=publicity)


@app.route("/xiangqing/<book_id>")
@app.route("/xiangqing")
def xiangqing(book_id):
    """
    详情页
    :param book_id:
    :return:
    """
    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    book = Book.query.filter(Book.id == book_id).first()
    sql = "select * from tf where b_id = '%s'" % str(book_id)
    data = SqlCx(sql)
    if len(data) == 0:
        sql = "select book_class from book where id=%s" % book_id
        book_class = SqlCx(sql)
        book_class = book_class[0]['book_class']
        data = FenLei(book_class)
    else:
        for i in data:
            data = str(i['tf']).replace(' ', '').split(',')
        sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'" \
              % (data[4], data[3], data[2], data[1], data[0])
        data = SqlCx(sql)
    print('用户点击---', session.get('username'), '-----', book.book_name)
    user_id = session.get('user_id')
    da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        sql = "insert into history values(null,%s,%s,'%s')" % (user_id, book_id, da)
        SqlCx(sql)

        sql = "select id from book_count where book_id=%s" % book_id
        d = SqlCx(sql)
        if d:
            print("data存在")
            sql = "update book_count set book_history=book_history+1 where book_id=%s" % book_id
            x = SqlCx(sql)
        else:
            print("data不存在")
            sql = "insert into book_count values(null,'" + book_id + "',1,0,0,0)"
            SqlCx(sql)
    except Exception as e:
        print('未登录用户正在查看----', book.book_name, e)
    collection = Collection.query.filter_by(book_id=book_id).count()
    history = History.query.filter_by(book_id=book_id).count()
    like = Like.query.filter_by(book_id=book_id).count()
    comment = Comment.query.filter_by(book_id=book_id).count()
    sql = "SELECT comment,data,username  FROM comment,user WHERE comment.book_id='%s' AND comment.user_id=user.id" % book_id
    comment_comment = SqlCx(sql)
    # sql = "SELECT * FROM user, comment WHERE comment.book_id='%s'"%book_id
    # comment_selsec = SqlCx(sql)
    sql = "SELECT COUNT(history.id) AS count, book_id, book_name FROM history,book WHERE book.id=history.book_id  GROUP BY book_id ORDER BY COUNT(history.id) DESC LIMIT 10"
    book_paihang = SqlCx(sql)
    sql = "SELECT COUNT(history.id) AS count, user_id, username FROM history,user WHERE user.id=history.user_id  GROUP BY user_id ORDER BY COUNT(history.id) DESC LIMIT 10"
    user_paihang = SqlCx(sql)
    return render_template("xiangqing.html", book=book, history=history, collection=collection, like=like,
                           comment=comment,
                           book_paihang=book_paihang, user_paihang=user_paihang, comment_comment=comment_comment,
                           data=data,
                           publicity=publicity)


@app.route("/comment/<book_id>")
@app.route("/comment")
def comment(book_id):
    """
    评论
    :param book_id:
    :return:
    """
    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    book = Book.query.filter(Book.id == book_id).first()
    sql = "select * from tf where b_id = '%s'" % str(book_id)
    data = SqlCx(sql)
    # print(data)
    if len(data) == 0:
        sql = "select book_class from book where id=%s" % book_id
        book_class = SqlCx(sql)
        book_class = book_class[0]['book_class']
        data = FenLei(book_class)
    else:
        for i in data:
            data = str(i['tf']).replace(' ', '').split(',')
        # print(data)
        sql = "select * from book where id='%s' or id='%s' or id='%s' or id='%s' or id='%s'" \
              % (data[4], data[3], data[2], data[1], data[0])
        data = SqlCx(sql)
    print('用户正在评论---', session.get('username'), '-----', book.book_name)
    user_id = session.get('user_id')
    # print(user_id)
    da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        new_history = History(user_id=int(user_id), book_id=int(book_id), id=None, data=da)
        db.session.add(new_history)
        db.session.commit()
    except:
        return render_template("loginerror.html")
    collection = Collection.query.filter_by(book_id=book_id).count()
    history = History.query.filter_by(book_id=book_id).count()
    like = Collection.query.filter_by(book_id=book_id).count()
    comment = Comment.query.filter_by(book_id=book_id).count()

    sql = "SELECT * FROM user, comment WHERE comment.book_id='%s'" % book_id
    comment_selsec = SqlCx(sql)
    sql = "SELECT COUNT(history.id) AS count, book_id, book_name FROM history,book WHERE book.id=history.book_id  GROUP BY book_id ORDER BY COUNT(history.id) DESC LIMIT 10"
    book_paihang = SqlCx(sql)
    sql = "SELECT COUNT(history.id) AS count, user_id, username FROM history,user WHERE user.id=history.user_id  GROUP BY user_id ORDER BY COUNT(history.id) DESC LIMIT 10"
    user_paihang = SqlCx(sql)
    return render_template("comment.html", book=book, history=history, collection=collection, like=like,
                           comment=comment, comment_comment=comment_selsec, publicity=publicity,
                           book_paihang=book_paihang, user_paihang=user_paihang, data=data)


@app.route("/comment/tj", methods=["POST"])
@app.route("/comment/tj/<int:book_id>", methods=["POST"])
def tijiao(book_id):
    """
    评论提交
    :param book_id:
    :return:
    """
    comment = request.form.get('comment')
    book_id = book_id
    user_id = session.get('user_id')
    # print(user_id)
    book = Book.query.filter(Book.id == book_id).first()
    print('用户正在评论---', session.get('username'), '-----', book.book_name, '----', comment)
    da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    new_comment = Comment(user_id=user_id, book_id=book_id, comment=comment, id=None, data=da)
    sql = "select id from book_count where book_id=%s" % book_id
    d = SqlCx(sql)
    if d:
        print("data存在")
        sql = "update book_count set book_comment=book_comment+1 where book_id=%s" % book_id
        SqlCx(sql)
    else:
        print("data不存在")
        sql = "insert into book_count values(null,'" + book_id + "',0,0,0,1)"
        SqlCx(sql)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for("xiangqing", book_id=book_id))


@app.route("/sousuo/<int:page>", methods=["GET"])
@app.route("/sousuo", methods=["POST"])
def sousuo(page=1):
    """
    搜索
    :param page:
    :return:
    """
    if request.method == "POST":
        publicity = "select * from publicity order by publicity.date desc"
        publicity = SqlCx(publicity)
        gjc = request.form.get('gjc')
        session['gjc'] = gjc
        print('用户搜索---', session.get('username'), '-----', gjc)
        book = Book.query.filter(Book.book_name.like("%" + gjc + "%")).all()
        data = SouSuo(gjc)
        if int(len(book) / 15) > len(book) / 15:
            page_num = int(len(book) / 15)
        else:
            page_num = int(len(book) / 15)
        page = int(page)
        if book:
            return render_template("sousuo.html", fenlei=book[(page - 1) * 15:(page * 15)], page_num=page_num,
                                   page=int(page), data=data, publicity=publicity)
        else:
            return render_template("sousuo.html", page=0)
    else:
        publicity = "select * from publicity order by publicity.date desc"
        publicity = SqlCx(publicity)
        gjc = session.get('gjc')
        data = SouSuo(gjc)
        book = Book.query.filter(Book.book_name.like("%" + gjc + "%")).all()
        print('用户搜索---', session.get('username'), '-----', gjc, '--', page)
        if int(len(book) / 15) > len(book) / 15:
            page_num = int(len(book) / 15)
        else:
            page_num = int(len(book) / 15)
        page = int(page)
        if book:
            return render_template("sousuo.html", fenlei=book[(page - 1) * 15:(page * 15)], page_num=page_num,
                                   page=int(page), data=data, publicity=publicity)
        else:
            return render_template("sousuo.html")


@app.route("/fenlei/<name>/<int:page>")
@app.route("/fenlei/<name>")
def fenlei2(name, page=1):
    """
    分类
    :param name: 分类名
    :param page: 页数
    :return:
    """
    publicity = "select * from publicity order by publicity.date desc"
    publicity = SqlCx(publicity)
    print('分类', session.get('username'), '-----', name)
    a = (page - 1) * 20
    sql = "select * from book where book_class='%s' limit %s,%s" % (name, a, 20)
    book = SqlCx(sql)
    sql = "select id from book where book_class='%s'" % name
    page_count = SqlCx(sql)
    data = FenLei(name)
    if int(len(page_count) / 20) > len(page_count) / 20:
        page_num = int(len(page_count) / 20)
    else:
        page_num = int(len(page_count) / 20)
    page = int(page)
    return render_template("fenlei.html", fenlei=book, page_num=page_num, page=int(page), data=data,
                           publicity=publicity)


@app.route("/tuichu")
def tuichu():
    """
    注销，推出登录
    :return:
    """
    print('用户退出', '-----', session.get('username'))
    session.clear()
    response = redirect(url_for("login"))
    response.delete_cookie('username')
    return response


@app.route("/reg", methods=["POST", "GET"])
def reg():
    """
    注册
    :return:
    """
    if request.method == 'POST':
        username = request.form.get('usn')
        account = request.form.get('account')
        password = request.form.get('pwd')
        password2 = request.form.get('pwd2')
        print('用户注册--', username)
        if password != password2:
            flash("两次输入密码不一致")
        elif len(password) > 8:
            flash("密码太长")
        elif len(str(username)) > 10:
            flash("昵称过长")
        elif Users.query.filter(Users.account == account).first():
            flash("账号已被注册")
        elif str(account).isdigit():
            # new_user = Users(username=username, account=account, password=password, id=None)
            # db.session.add(new_user)
            # db.session.commit()
            da = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            sql = "insert into user values(null,'" + str(username) + "','" + \
                  str(account) + "','" + str(password) + "',null,null,0,0,0,null,null,null,null,'" + str(da) + "')"
            SqlCx(sql)
            return redirect(url_for("login"))
        else:
            flash("账号由纯数字组成")
    else:
        return render_template("reg.html")
    return render_template("reg.html")


@app.errorhandler(404)
def page_not_found(e):
    """
    404
    :param e:
    :return:
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    500
    :param e:
    :return:
    """
    return render_template('500.html'), 500



if __name__ == '__main__':
    app.run(debug=True)
