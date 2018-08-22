# -*- coding: utf-8 -*-

from flask import render_template

from . import index


@index.route('/login2ore4manageSystem')
def login():
    return render_template('login/login.html')