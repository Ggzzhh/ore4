# -*- coding: utf-8 -*-

from flask import flash, redirect, url_for, jsonify, \
    current_app, request, abort, session
from flask_login import logout_user, current_user, login_required

from . import api_v1
from ..handle_excel import MakeExcel
from ..models import db, User, Role, Duty, DutyLevel, Dept, \
    Personnel, State, Resume, Title, Education, RAndP, Family
from ..personnel.views import filter_query
from ..tools import replace2none, str2time, filter_field
from ..index.views import per_info_count


@api_v1.route('/field', methods=["POST"])
@login_required
def update_field():
    res = request.get_json()
    if res is None:
        return jsonify({'error': True, 'error_message': '没有值传递'})
    fields = res.get('fields')
    user = current_user.set_fields(fields)
    db.session.add(user)
    return jsonify({'error': False, 'message': '操作成功！'})


@api_v1.route('/manage-per', methods=["POST"])
@login_required
def manage_per():
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    res = request.get_json()
    if res is None:
        return jsonify({'error': True, 'error_message': '没有值传递'})
    res = replace2none(res)
    info = res.get('info')
    if info:
        _id = res.get('id')
        name = info.get('name')
        id_card = info.get('id_card')
        dept = Dept.query.get(info.get('dept_name'))
        state = State.query.get(info.get('state'))
        duty = Duty.from_json({'name': info.get('duty'),
                               'duty_level_id': info.get('duty_lv')})
        if name is None:
            abort(403)
        if id_card is not None:
            id_card = Personnel.query.filter_by(id_card=id_card).first()
            if id_card is not None:
                return jsonify({'error': True, 'error_message': '身份证号已存在! '
                                                                '不可重复！'})
        if _id:
            per = Personnel.query.get_or_404(_id)
            per.from_json(info, _id)
        else:
            per = Personnel.from_json(info)

        if dept:
            per.dept = dept

        if state:
            per.state = state

        if duty:
            per.duty = duty

        for resume in res.get('resumes'):
            resume = Resume.from_json(resume)
            if resume and resume not in per.resumes:
                per.resumes.append(resume)

        for title in res.get('titlies'):
            title = Title.from_json(title)
            if title and title not in per.titlies:
                per.titlies.append(title)

        for edu in res.get('edus'):
            edu = Education.from_json(edu)
            if edu and edu not in per.edus:
                per.edus.append(edu)

        for rp in res.get('r_and_p'):
            rp = RAndP.from_json(rp)
            if rp and rp not in per.r_and_ps:
                per.r_and_ps.append(rp)

        for family in res.get('families'):
            family = Family.from_json(family)
            if family and family not in per.families:
                per.families.append(family)

        per.max_edu_id = per.max_edu.edu_level.id if per.max_edu else None
        per.at_edu_id = per.at_edu.edu_level.id if per.at_edu else None
        per.ot_edu_id = per.ot_edu.edu_level.id if per.ot_edu else None
        per.use_title_id = per.use_title()
        per.use_title_name_id = per.use_title_name()

        db.session.add(per)
        return jsonify({'error': False, 'message': '操作成功！'})
    return jsonify({'error': True, 'error_message': '未知错误!'})


@api_v1.route('/update-pwd', methods=["POST"])
@login_required
def update_pwd():
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    res = request.get_json()
    if res is None:
        return jsonify({'error': True, 'error_message': '没有值传递'})
    user = User.query.get_or_404(res['id'])
    if user and res['old_pwd']:
        if user.verify_password(res['old_pwd']):
            user.password = res['pwd']
            db.session.add(user)
            return jsonify({'error': False, 'message': '密码更改成功！'})
    return jsonify({'error': True, 'error_message': '密码错误！'})


@api_v1.route('/manage-user', methods=['POST', 'DELETE'])
@login_required
def manage_user():
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    res = request.get_json()
    if res is None:
        return jsonify({'error': True, 'error_message': '没有值传递'})
    if request.method == "POST":
        if res['new']:
            if User.query.filter_by(username=res['username']).first():
                return jsonify({'error': True, 'error_message': '用户已存在'})
            user = User(username=res['username'])
            user.role = Role.query.filter_by(name='审查者').first()
            message = '新增了一名审查者-用户名: {}, 密码: {}'.format(res['username'],
                                                        res['password'])
        else:
            user = User.query.get_or_404(res['id'])
            message = '密码更改成功！'
        user.password = res['password']
        db.session.add(user)
    elif request.method == "DELETE":
        user = User.query.get_or_404(res['id'])
        db.session.delete(user)
        message = '删除成功'
    return jsonify({'error': False, 'message': message})


@api_v1.route('/manage-duty', methods=['POST', 'DELETE'])
@login_required
def manage_duty():
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    res = request.get_json()
    if res is None:
        return jsonify({'error': True, 'error_message': '没有值传递'})
    if request.method == "POST":
        lv = DutyLevel.query.get_or_404(res['lv_id'])
        if res['new']:
            duty = Duty(name=res['name'])
            message = '添加职务成功!'
        else:
            duty = Duty.query.get_or_404(res.get('id'))
            duty.name = res['name']
            message = '修改职务成功!'
        if duty and lv:
            duty.duty_level = lv
            duty.order = res.get('order')
        db.session.add(duty)
    elif request.method == "DELETE":
        duty = Duty.query.get_or_404(res['id'])
        db.session.delete(duty)
        message = '删除成功'
    return jsonify({'error': False, 'message': message})


@api_v1.route('/manage-dept', methods=['POST', 'DELETE'])
@login_required
def manage_dept():
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    res = request.get_json()
    message = ''
    if res is None:
        return jsonify({'error': True, 'error_message': '没有值传递'})
    if request.method == "POST":
        temp, add = Dept.from_json(res)
        if add and temp:
            message = '新增成功!'
        elif add is False and temp:
            message = '修改成功'
        else:
            return jsonify({'error': True, 'error_message': '发生错误！请联系维护人员！'})
        db.session.add(temp)
    elif request.method == "DELETE":
        dept = Dept.query.get_or_404(res['id'])
        db.session.delete(dept)
        message = '删除成功'
    return jsonify({'error': False, 'message': message})


@api_v1.route('/logout/<string:username>')
@login_required
def logout(username):
    if username == current_user.username:
        logout_user()
        flash('账号已注销！')
    return redirect(url_for('index.login'))


@api_v1.route('/del-user/<int:id>')
@login_required
def del_user(id):
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    user = User.query.get_or_404(id)
    db.session.delete(user)
    return jsonify({'error': False, 'message': '已删除!'})


@api_v1.route('/del-resume/<int:id>', methods=["DELETE"])
@login_required
def del_resume(id):
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    resume = Resume.query.get_or_404(id)
    db.session.delete(resume)
    return jsonify({'error': False, 'message': '已删除!'})


@api_v1.route('/del-title/<int:id>', methods=["DELETE"])
@login_required
def del_title(id):
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    title = Title.query.get_or_404(id)
    db.session.delete(title)
    return jsonify({'error': False, 'message': '已删除!'})


@api_v1.route('/del-edu/<int:id>', methods=["DELETE"])
@login_required
def del_edu(id):
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    edu = Education.query.get_or_404(id)
    db.session.delete(edu)
    return jsonify({'error': False, 'message': '已删除!'})


@api_v1.route('/del-r-and-p/<int:id>', methods=["DELETE"])
@login_required
def del_r_and_p(id):
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    r_and_p = RAndP.query.get_or_404(id)
    db.session.delete(r_and_p)
    return jsonify({'error': False, 'message': '已删除!'})


@api_v1.route('/del-family/<int:id>', methods=["DELETE"])
@login_required
def del_family(id):
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    family = Family.query.get_or_404(id)
    db.session.delete(family)
    return jsonify({'error': False, 'message': '已删除!'})


@api_v1.route('/save-img', methods=["POST"])
@login_required
def save_img():
    data = request.get_data()
    print(data)
    return jsonify({"data": "/static/image/timg.jpg"})


@api_v1.route('/punished', methods=["UPDATE"])
@login_required
def punished():
    data = request.get_json()
    ids = data.get('ids')
    if ids is not None and ids != []:
        for _id in ids:
            per = Personnel.query.get(_id)
            if per is not None:
                if per.punished is None:
                    per.punished = False
                per.punished = not per.punished
                db.session.add(per)
            else:
                jsonify({'error': True, 'error_message': '数据出错!'})
        return jsonify({'error': False, 'message': '调配完成!'})
    else:
        return jsonify({'error': False, 'message': '没有选择调配目标!'})


@api_v1.route('/choice-state', methods=["UPDATE"])
@login_required
def choice_state():
    data = request.get_json()
    ids = data.get('ids')
    _state = data.get('state')
    if ids is not None and ids != []:
        for _id in ids:
            per = Personnel.query.get(_id)
            if per is not None:
                state = State.query.get(int(_state))
                print(_state)
                if state:
                    per.state = state
                else:
                    jsonify({'error': True, 'error_message': '数据出错!'})
                db.session.add(per)
            else:
                jsonify({'error': True, 'error_message': '数据出错!'})
        return jsonify({'error': False, 'message': '调配完成!'})
    else:
        return jsonify({'error': False, 'message': '没有选择调配目标!'})


@api_v1.route('/work-move', methods=["UPDATE"])
@login_required
def work_move():
    data = request.get_json()
    _id = data.get('id')
    dept_id = data.get('dept_id')
    duty_name = data.get('duty_name')
    duty_lv = data.get('duty_lv')
    identifier = data.get('identifier')
    work_time = str2time(data.get('work_time'))
    if _id is not None and _id != "":
        per = Personnel.query.get(_id)
        last_dept = per.dept
        last_duty = per.duty
        if last_dept:
            last_dept = last_dept.dept_name
        if last_duty:
            last_duty = last_duty.name
        last_resume = Resume.query.filter(Resume.dept==last_dept,
                                          Resume.duty==last_duty).first()
        if last_resume is None:
            last_resume = Resume(dept=last_dept, duty=last_duty)
        last_resume.change_time = work_time

        dept = Dept.query.get_or_404(dept_id)
        duty = Duty.query.filter_by(name=duty_name).first()
        if duty is None:
            duty = Duty(name=duty_name)
        duty_lv = DutyLevel.query.get_or_404(duty_lv)
        duty.duty_level = duty_lv
        per.dept = dept
        per.duty = duty
        resume = Resume(dept=dept.dept_name, duty=duty.name)
        resume.identifier = identifier
        resume.work_time = work_time
        per.resumes.append(last_resume)
        per.resumes.append(resume)
        db.session.add(per)
        return jsonify({'error': False, 'message': '调配完成!'})
    else:
        return jsonify({'error': False, 'message': '没有选择调配目标!'})


@api_v1.route('/del_per', methods=["DELETE"])
@login_required
def del_per():
    data = request.get_json()
    ids = data.get('ids')
    if ids is not None and ids != []:
        for _id in ids:
            per = Personnel.query.get(_id)
            if per is not None:
                db.session.delete(per)
            else:
                jsonify({'error': True, 'error_message': '数据出错!'})
        return jsonify({'error': False, 'message': '删除成功!'})
    else:
        return jsonify({'error': False, 'message': '没有选择目标!'})


@api_v1.route('/make_excel/<val>')
@login_required
def make_excel(val):
    query = Personnel.query.join(Duty)
    if val == 'all':
        query = filter_query(query, is_none=False, is_all=True)
    elif val == 'is_none':
        query = filter_query(query, is_none=False)
    else:
        session['val'] = val
        query = filter_query(query)
    pers = query.order_by(Duty.order, Duty.duty_level_id.desc()).all()
    fields = current_user.get_fields()
    me = MakeExcel(fields=fields, file_name='查询结果.xls')
    pers = filter_field(pers, fields)
    try:
        filename = me.make_result_file(pers)
        url = url_for('index.download', filename=filename)
    except PermissionError:
        return jsonify({'error': True,
                        'error_message': '生成文件失败, '
                                         '请先关闭当前名为“查询结果.xls”的文件或者重命名!!'})
    else:
        return jsonify({'error': False,
                        'message': '导出成功！即将开始下载！',
                        'url': url})


@api_v1.route('/make_roster', methods=["POST"])
@login_required
def make_roster():
    data = request.get_json()
    ids = data.get('ids')
    me = MakeExcel(file_name='干部花名册.xls')
    if ids is not None and ids != []:
        try:
            filename = me.make_roster_file(ids)
            url = url_for('index.download', filename=filename)
        except PermissionError:
            return jsonify({'error': True,
                            'error_message': '生成文件失败, '
                                             '请先关闭当前名为“干部花名册.xls”的文件或者重命名!!'})
        else:
            return jsonify({'error': False,
                            'message': '导出成功！即将开始下载！',
                            'url': url})
    return jsonify({'error': True,
                    'error_message': '请选择至少一个单位！'})


@api_v1.route('/make-census')
def make_census():
    try:
        me = MakeExcel(file_name="人数统计.xls")
        per_info_count("duty")
        per_info_count("dept")
        per_info_count("title")
        per_info_count("state")
        filename = me.make_count_excel()
        url = url_for('index.download', filename=filename)
    except PermissionError:
        return jsonify({'error': True,
                        'error_message': '生成文件失败, '
                                         '请先关闭当前名为“干部花名册.xls”的文件或者重命名!!'})
    else:
        return jsonify({'error': False,
                        'message': '导出成功！即将开始下载！',
                        'url': url})