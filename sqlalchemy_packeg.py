# coding:utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), default='易水寒')
    account = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    perference = db.Column(db.String(50), nullable=True)
    major = db.Column(db.String(50), nullable=True)


class Collection(db.Model):
    __tablename__ = 'collection'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    data = db.Column(db.TIMESTAMP)


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_name = db.Column(db.VARCHAR(100), nullable=False)
    book_author = db.Column(db.CHAR(50))
    book_abstract = db.Column(db.String(1000))
    book_class = db.Column(db.VARCHAR(50))
    book_img = db.Column(db.CHAR(50))
    book_link = db.Column(db.VARCHAR(50))


class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    data = db.Column(db.TIMESTAMP)


class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    data = db.Column(db.TIMESTAMP)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    comment = db.Column(db.String(100))
    data = db.Column(db.TIMESTAMP)


class Yueduhistory(db.Model):
    __tablename__ = 'yuedu_history'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_name = db.Column(db.VARCHAR(100), nullable=False)
    url = db.Column(db.String(100))
    data = db.Column(db.TIMESTAMP)
