import time
import json
from datetime import datetime, timedelta

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel
from sqlalchemy import or_, and_

from . import index
from ..models import User, Dept, System, Title, Duty, DutyLevel, \
    DeptPro, Personnel, Field
from ..const import NAV, FIELDS
from ..tools import filter_field


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
    nav_data = NAV

    systems = System.query.order_by("id").all()

    return render_template('index.html', nav=nav_data, systems=systems)


@index.route('/search', methods=["POST", "GET"])
@login_required
def search():
    page = request.args.get('page', 1, type=int)
    dept_names = Dept.to_arr()
    duty_lvs = DutyLevel.to_array()
    all_fields = list(FIELDS.keys())
    fields = Field.fields()
    if request.method == "GET":
        base_query = Personnel.query.join(Duty, Duty.id == Personnel.duty_id)
        dept_id = request.args.get('dept_id')
        if dept_id:
            base_query = base_query.filter(Personnel.dept_id == dept_id)
        pagination = base_query.order_by(Duty.order, Duty.duty_level_id.desc())\
            .paginate(
            page, per_page=current_app.config['SEARCH_PAGE'],
            error_out=False
        )
    else:
        form = request.form
        val = form['easy_search']
        if val is None or val == '':
            return redirect(url_for('index.search'))
        query = Personnel.query.filter(
            or_(
                Personnel.name.like('%' + val + '%'),
                Personnel.phonetic.like('%' + val + '%')
            )
        )
        pagination = query.order_by(Duty.order, Duty.duty_level_id.desc()) \
            .paginate(
            page, per_page=current_app.config['SEARCH_PAGE'],
            error_out=False)
    pers = pagination.items
    pers = filter_field(pers, fields)
    return render_template('search.html', fields=fields, pers=pers,
                           all_fields=all_fields, pagination=pagination,
                           dept_names=dept_names, duty_lvs=duty_lvs,
                           dept_id=dept_id)


@index.route('/search-criteria', methods=["GET", "POST"])
@login_required
def search_criteria():
    page = request.args.get('page', 1, type=int)
    fields = Field.fields()
    dept_names = Dept.to_arr()
    duty_lvs = DutyLevel.to_array()
    all_fields = list(FIELDS.keys())
    if request.method == "POST":
        form = request.form
        pagination = Personnel.query.join(Duty, Duty.id == Personnel.duty_id) \
            .order_by(Duty.order, Duty.duty_level_id.desc()).paginate(
            page, per_page=current_app.config['SEARCH_PAGE'],
            error_out=False
        )
    pers = pagination.items
    pers = filter_field(pers, fields)

    return render_template('search.html', fields=fields, pers=pers,
                           all_fields=all_fields, pagination=pagination,
                           dept_names=dept_names, duty_lvs=duty_lvs)


@index.route('/system-manage/user')
@login_required
def system_manage_user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.filter(User.id != 1).order_by(
        User.id).paginate(
        page, per_page=current_app.config['PER_PAGE'],
        error_out=False
    )
    users = pagination.items

    return render_template('system_manage/user.html', title='用户管理',
                           users=users, pagination=pagination)


@index.route('/system-manage/duty')
@login_required
def system_manage_duty():
    duties = []
    page = request.args.get('page', 1, type=int)
    pagination = Duty.query.order_by(Duty.order,
                                     Duty.duty_level_id.desc()).paginate(
        page, per_page=current_app.config['PER_PAGE'],
        error_out=False
    )
    for duty in pagination.items:
        duties.append(duty.to_json())
    lvs = DutyLevel.to_array()
    return render_template('system_manage/duty.html', title='职务管理', lvs=lvs,
                           duties=duties, pagination=pagination)


@index.route('/system-manage/dept')
@login_required
def system_manage_dept():
    depts = []
    page = request.args.get('page', 1, type=int)
    pagination = Dept.query.order_by(Dept.order, Dept.dept_pro_id).paginate(
        page, per_page=current_app.config['PER_PAGE'],
        error_out=False
    )
    for dept in pagination.items:
        depts.append(dept.to_json())
    systems = System.to_array()
    dept_pros = DeptPro.to_array()
    return render_template('system_manage/dept.html', title='单位管理',
                           systems=systems, dept_pros=dept_pros,
                           depts=depts, pagination=pagination)


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