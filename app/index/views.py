import time
import json
from datetime import datetime, timedelta

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel

from . import index
from ..models import User, Dept, System, Title, Duty


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
                    error_messgae = '密码错误，今日还可尝试{}次！' \
                        .format(user.retry_count)
        else:
            error_messgae = '用户不存在！'
        return render_template('login/login.html',
                               system_name=current_app.config['SYSTEMNAME'],
                               error_message=error_messgae)
    return render_template('login/login.html',
                           system_name=current_app.config['SYSTEMNAME'])


@index.route('/main')
@login_required
def main():
    nav_data = {
        '人员信息': {
            'id': 'dropdown_info',
            'data': {
                '新增人员': '#',
                'excel录入': '#',
                '照片导入': '#'
            }
        },
        '统计查询': {
            'id': 'dropdown_search',
            'data': {
                '姓名查询': '#',
                '系统查询': '#',
                '单位查询': '#',
                '年龄查询': '#',
                '职务查询': '#',
                'divider': '#',
                '职务统计': '#',
                '单位统计': '#',
                '职称统计': '#',
                '状态统计': '#'
            }
        },
        '报表整理': {
            'id': 'dropdown_table',
            'data': {
                '干部花名册': '#',
                '人数统计表': '#'
            }
        },
        '系统管理': {
            'id': 'dropdown_system',
            'data': {
                '用户管理': 'm_user',
                '职务管理': 'm_duty',
                '职称管理': 'm_title',
                '参数管理': '#',
                'divider': '#',
                '修改密码': 'update_password'
            }
        }
    }

    systems = System.query.order_by("id").all()

    return render_template('index.html', nav=nav_data, systems=systems)


@index.route('/search')
@login_required
def search():
    l = [i for i in range(1, 19)]
    user = {
        'name': '张三',
        'mz': '汉',
        'sex': '男',
        'birthday': '19930113',
    }
    dic = {
        1: ['name', '姓名'],
        2: ['mz', '民族'],
        3: ['sex', '性别'],
        4: ['birthday', '生日'],
        5: ['birthday', '生日'],
        6: ['birthday', '生日'],
        7: ['birthday', '生日'],
        8: ['birthday', '生日'],
        9: ['birthday', '生日'],
        10: ['birthday', '生日'],
        11: ['birthday', '生日'],
        12: ['birthday', '生日'],
        13: ['birthday', '生日'],
        14: ['birthday', '生日'],
        15: ['birthday', '生日'],
        16: ['birthday', '生日'],
        17: ['birthday', '生日'],
        18: ['birthday', '生日'],
    }
    return render_template('search.html', user=user, dic=dic, l=l)


@index.route('/system-manage/user')
@login_required
def system_manage_user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.filter(User.id > 1).order_by(User.id).paginate(
        page, per_page=current_app.config['PER_PAGE'],
        error_out=False
    )
    users = pagination.items

    return render_template('system_manage/user.html', title='用户管理',
                           users=users, pagination=pagination)


@index.route('/system-manage/title')
@login_required
def system_manage_title():
    titles = []
    page = request.args.get('page', 1, type=int)
    pagination = Title.query.order_by(Title.id).paginate(
        page, per_page=current_app.config['PER_PAGE'],
        error_out=False
    )
    for title in pagination.items:
        titles.append(title.to_json())
    return render_template('system_manage/title.html', title='职称管理',
                           titles=titles, pagination=pagination)


@index.route('/system-manage/pwd')
@login_required
def system_manage_pwd():
    return render_template('system_manage/pwd.html', title='修改密码')


@index.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        return jsonify({'result': request.get_array(field_name='file')})
    user = current_user.username
    return render_template('test.html')
    # return '''
    # <!doctype html>
    # <title>Upload an excel file %s </title>
    # <h1>Excel file upload (csv, tsv, csvz, tsvz only)</h1>
    # <form action="" method=post enctype=multipart/form-data><p>
    # <input type=file name=file><input type=submit value=Upload>
    # </form>
    # ''' % user


@index.route("/test", methods=['GET'])
def test():
    return jsonify('我擦asdasd123')


@index.route("/download", methods=['GET'])
@login_required
def download_file_named_in_unicode():
    return excel.make_response_from_array([['呵呵呵', '哈哈哈'], ['哟啊', 4]], "xlsx",
                                          file_name=u"中文文件名")