# -*- coding: utf-8 -*-
import time
import json
from datetime import datetime, timedelta

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel

from . import index
from ..models import User


@index.route('/login2ore4manageSystem', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = request.form
        username, password = form['username'], form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None:
            if user.disable_time and \
                            user.disable_time.day >= datetime.now().day:
                error_messgae = '该账号已被锁定！解锁时间{}!'.format(
                    user.disable_time.date() + timedelta(days=1))
            else:
                if user.disable_time and user.disable_time.day < \
                        datetime.now().day:
                    user.disable_time = None
                    user.retry_count = 10
                if user.verify_password(password):
                    login_user(user)
                    return redirect(request.args.get('next') or url_for(
                        'index.main'))
                else:
                    user.retry_count -= 1
                    if user.retry_count == 0:
                        user.disable_time = datetime.now()
                        error_messgae = '账号被锁定'
                    error_messgae = '密码错误，今日还可尝试{}次！'\
                        .format(user.retry_count)
        else:
            error_messgae = '用户不存在！'
        return render_template('login/login.html',
                               system_name=current_app.config['SYSTEMNAME'],
                               error_message=error_messgae)
    # if current_user:
    #     return redirect(url_for('index.upload'))
    return render_template('login/login.html',
                           system_name=current_app.config['SYSTEMNAME'])


@index.route('/')
@login_required
def main():
    return render_template('index.html', date=datetime.utcnow())


@index.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        return json.dumps({'result': request.get_array(field_name='file')},
                          ensure_ascii=False)
    user = current_user.username
    return '''
    <!doctype html>
    <title>Upload an excel file %s </title>
    <h1>Excel file upload (csv, tsv, csvz, tsvz only)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    ''' % user


@index.route("/export", methods=['GET'])
def export_records():
    return excel.make_response_from_array([[1, 2], [3, 4]], "xlsx",
                                          file_name="export_data")


@index.route("/download", methods=['GET'])
@login_required
def download_file_named_in_unicode():
    return excel.make_response_from_array([['呵呵呵', '哈哈哈'], ['哟啊', 4]], "xlsx",
                                          file_name=u"中文文件名")