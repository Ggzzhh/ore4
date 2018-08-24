# -*- coding: utf-8 -*-
from datetime import timedelta

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_moment import Moment
import flask_excel as excel

from config import config

# 实例化各个组件
bootstrap = Bootstrap()
login_manager = LoginManager()
db = SQLAlchemy()
csrf = CsrfProtect()
moment = Moment()


# 登陆相关设置
login_manager.session_protection = "strong"
login_manager.login_view = "index.login"
login_manager.login_message = "请登录后访问！"
login_manager.login_message_category = "info"
login_manager.remember_cookie_duration = timedelta(days=1)


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    excel.init_excel(app)
    moment.init_app(app)

    # 设置session设置的过期时间 也就是关闭浏览器5分钟内不用重新登录
    app.permanent_session_lifetime = timedelta(minutes=60)

    # 在正常使用时打开ssl安全协议
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app=app)

    # 注册蓝图
    from .index import index as index_blueprint
    app.register_blueprint(index_blueprint)

    from .api_v1 import api_v1 as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix="/v1")


    return app

