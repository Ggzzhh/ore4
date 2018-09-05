# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel

from . import per


@per.route('/add')
@login_required
def add_per():
    return render_template('per/add.html', title='新增人员', user='测试')