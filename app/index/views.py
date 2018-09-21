import time
import json
from datetime import datetime, timedelta

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, session
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel
from sqlalchemy import or_, and_

from . import index
from ..models import User, Dept, System, Title, Duty, DutyLevel, \
    DeptPro, Personnel, State, TitleName, TitleLv, TitleDept
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
    fields = current_user.get_fields()
    dept_id = request.args.get('dept_id')
    if request.method == "GET":
        base_query = Personnel.query.join(Duty)
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
                           dept_id=dept_id, endpoint='index.search')


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


@index.route('/per-info-count/<string:info>')
@login_required
def per_info_count(info):
    title = None
    content = []
    pers = Personnel.query.all()
    session['count'] = {}

    if info == "duty":
        title = "职务统计"
        cls = {"title": "职务等级", "fields": [], 'count': 0}
        lvs = DutyLevel.query.order_by(DutyLevel.id.desc()).all()
        for lv in lvs:
            count = 0
            for per in pers:
                if per.duty and per.duty.duty_level_id == lv.id:
                    count += 1
            field = {
                'name': lv.name,
                'count': count
            }
            cls['fields'].append(field)
            cls['count'] += field['count']
        content.append(cls)
        session['count']['职务统计'] = cls

    if info == "dept":
        title = "单位统计"
        cls_name = {"title": "单位简称", "fields": [], 'count': 0}
        cls_pro = {"title": "单位属性", "fields": [], 'count': 0}
        cls_system = {"title": "单位系统", "fields": [], 'count': 0}
        names = Dept.query.order_by(Dept.id).all()
        pros = DeptPro.query.order_by(DeptPro.id).all()
        systems = System.query.order_by(System.id).all()

        for name in names:
            field = {
                'name': name.dept_name,
                'count': 0,
                'id': name.id
            }
            cls_name['fields'].append(field)

        for pro in pros:
            field = {
                'name': pro.dept_pro_name,
                'count': 0,
                'id': pro.id
            }
            cls_pro['fields'].append(field)

        for system in systems:
            field = {
                'name': system.system_name,
                'count': 0,
                'id': system.id
            }
            cls_system['fields'].append(field)

        for per in pers:
            for name in cls_name['fields']:
                if per.dept_id == name['id']:
                    name['count'] += 1
                    cls_name['count'] += 1

            for pro in cls_pro['fields']:
                if per.dept and per.dept.dept_pro_id == pro['id']:
                    pro['count'] += 1
                    cls_pro['count'] += 1

            for system in cls_system['fields']:
                if per.dept and per.dept.system_id == system['id']:
                    system['count'] += 1
                    cls_system['count'] += 1

        content.append(cls_name)
        content.append(cls_pro)
        content.append(cls_system)

    if info == "title":
        title = "职称统计"
        cls_name = {"title": "职称名称", "fields": [], 'count': 0}
        cls_lv = {"title": "职称等级", "fields": [], 'count': 0}
        cls_dept = {"title": "职称系列", "fields": [], 'count': 0}
        cls_major = {"title": "职称专业", "fields": [], 'count': 0}
        names = TitleName.query.order_by(TitleName.id).all()
        lvs = TitleLv.query.order_by(TitleLv.id).all()
        depts = TitleDept.query.order_by(TitleDept.id).all()

        for name in names:
            field = {
                'name': name.name,
                'count': 0,
                'id': name.id
            }
            cls_name['fields'].append(field)

        for lv in lvs:
            field = {
                'name': lv.name,
                'count': 0,
                'id': lv.id
            }
            cls_lv['fields'].append(field)

        for dept in depts:
            field = {
                'name': dept.name,
                'count': 0,
                'id': dept.id
            }
            cls_dept['fields'].append(field)

        titlies = Title.query.all()
        for _title in titlies:
            exist = False
            for major in cls_major['fields']:
                if major['name'] == _title.major:
                    exist = True
                    major['count'] += 1
                    cls_major['count'] += 1
            if exist is False and _title.major:
                if _title.major == "":
                    break
                temp = {
                    'name': _title.major,
                    'count': 1,
                    'id': 0
                }
                cls_major['fields'].append(temp)
                cls_major['count'] += 1

            for dept in cls_dept['fields']:
                if _title.name.title_dept_id == dept['id']:
                    dept['count'] += 1
                    cls_dept['count'] += 1

            for lv in cls_lv['fields']:
                if _title.name.title_lv_id == lv['id']:
                    lv['count'] += 1
                    cls_lv['count'] += 1

            for name in cls_name['fields']:
                if _title.name_id == name['id']:
                    name['count'] += 1
                    cls_name['count'] += 1

        content.append(cls_name)
        content.append(cls_dept)
        content.append(cls_lv)
        content.append(cls_major)

    if info == "state":
        title = "状态统计"
        cls = {"title": "员工状态", "fields": [], 'count': 0}
        states = State.query.order_by(State.id).all()
        for state in states:
            field = {
                'name': state.name,
                'count': 0,
                'id': state.id
            }
            cls['fields'].append(field)
        for per in pers:
            for field in cls['fields']:
                if per.state and field['id'] == per.state.id:
                    field['count'] += 1
                    cls['count'] += 1
        content.append(cls)

    return render_template('per_info_count.html', title=title, content=content)


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