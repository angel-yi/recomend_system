# coding=utf-8
# !/usr/bin/python
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from app import app

print("开始启动flask程序")
http_server = HTTPServer(WSGIContainer(app))
print("端口5000")
http_server.listen(5000)
IOLoop.instance().start()
print("flask程序启动完成")
