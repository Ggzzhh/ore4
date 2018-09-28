# -*- coding: utf-8 -*-deactivate
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from manage import app
from config import PORT

http_server = HTTPServer(WSGIContainer(app))
print('服务启动成功! 端口：{}'.format(PORT))
http_server.listen(PORT)
try:
    IOLoop.instance().start()
except KeyboardInterrupt:
    IOLoop.instance().stop()