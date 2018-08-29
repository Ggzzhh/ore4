# -*- coding: utf-8 -*-

from flask import flash, redirect, url_for
from flask_login import logout_user, current_user, login_required

from . import api_v1
from ..models import User


@api_v1.route('/')
def test():
    return "欢迎来到英雄联盟"


@api_v1.route('/logout/<string:username>')
@login_required
def logout(username):
    if username == current_user.username:
        logout_user()
        flash('账号已注销！')
    return redirect(url_for('index.login'))