# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, flash, session
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel
from sqlalchemy import text, or_

from . import per
from ..const import FIELDS
from ..tools import filter_field, str2time
from ..models import EduLevel, LearnForm, TitleName, DeptPro, TitleDept,\
    Dept, DutyLevel, State, Personnel, Nation, System, Duty, Education, \
    TitleLv, Title


@per.route('/roster')
@login_required
def roster():
    systems = System.query.order_by(System.id).all()
    return render_template('search/roster.html', systems=systems)


@per.route('/add')
@login_required
def add_per():
    edu_lv = EduLevel.to_arr()
    learn_form = LearnForm.to_arr()
    title_names = TitleName.to_arr()
    dept_names = Dept.to_arr()
    duty_lvs = DutyLevel.to_array()
    states = State.to_arr()
    nations = Nation.to_arr()
    return render_template('per/personnel.html', title='新增人员', edu_lv=edu_lv,
                           learn_form=learn_form, title_names=title_names,
                           dept_names=dept_names, duty_lvs=duty_lvs,
                           nations=nations, states=states, form_id='add-per',
                           per={}, enumerate=enumerate)


@per.route('/edit/per/<int:_id>')
@login_required
def edit_per(_id):
    edu_lv = EduLevel.to_arr()
    learn_form = LearnForm.to_arr()
    title_names = TitleName.to_arr()
    dept_names = Dept.to_arr()
    duty_lvs = DutyLevel.to_array()
    states = State.to_arr()
    nations = Nation.to_arr()
    per = Personnel.query.get_or_404(_id)
    f_count = 0
    r_and_p_count = 0
    edu_count = 0
    title_count = 0
    resume_count = 0

    if per is not None:
        per = per.to_json()
        f_count = len(per['families'])
        r_and_p_count = len(per['r_and_ps'])
        edu_count = len(per['edus'])
        title_count = len(per['titlies'])
        resume_count = len(per['resumes'])
    else:
        per = None

    return render_template('per/personnel.html', title='人员信息', edu_lv=edu_lv,
                           learn_form=learn_form, title_names=title_names,
                           dept_names=dept_names, duty_lvs=duty_lvs,
                           states=states, per=per, form_id='edit-per',
                           f_count=f_count, r_and_p_count=r_and_p_count,
                           edu_count=edu_count, title_count=title_count,
                           resume_count=resume_count, enumerate=enumerate,
                           nations=nations)


@per.route('/condition-search')
@login_required
def condition_search():
    systems = System.query.order_by('id').all()
    nations = Nation.to_arr()
    pros = DeptPro.to_array()
    lvs = DutyLevel.to_array()
    edu_lvs = EduLevel.to_arr()
    states = State.to_arr()
    title_lvs = TitleLv.to_arr()
    title_depts = TitleDept.to_arr()
    title_names = TitleName.to_arr()
    return render_template('search/condition.html', systems=systems,
                           nations=nations, pros=pros, lvs=lvs,
                           edu_lvs=edu_lvs, states=states, title_lvs=title_lvs,
                           title_names=title_names, title_depts=title_depts)


@per.route('/search-result',  methods=["POST", "GET"])
@login_required
def search_result():
    if request.method == "POST":
        form = request.form
        is_none = True
        # print(form)

        for e in form:
            if form[e] != '':
                is_none = False
                break

        try:
            age1 = int(form.get('age1', 0))
            age2 = int(form.get('age2', 0))
            min_age = min([age1, age2])
            max_age = max([age1, age2])
            session['min_age'] = min_age
            session['max_age'] = max_age
        except:
            pass

        session['re_name'] = r'{}'.format(form.get('name', ''))
        session['re_phonetic'] = r'{}'.format(form.get('phonetic', ''))
        session['re_sex'] = r'{}'.format(form.get('sex', ''))
        session['re_nation'] = r'{}'.format(form.get('nation', ''))
        session['re_id_card'] = r'{}'.format(form.get('id_card', ''))
        session['re_cadre_id'] = r'{}'.format(form.get('cadre_id', ''))
        session['re_policital_status'] = r'{}'.format(form.get('policital_status', ''))
        session['re_native_place'] = r'{}'.format(form.get('native_place', ''))
        session['re_birth_place'] = r'{}'.format(form.get('birth_place', ''))
        session['re_identity'] = r'{}'.format(form.get('identity', ''))
        session['re_work_no'] = r'{}'.format(form.get('work_no', ''))
        session['re_work_year'] = r'{}'.format(form.get('work_year', ''))
        session['re_major'] = r'{}'.format(form.get('major', ''))
        session['re_duty'] = r'{}'.format(form.get('duty', ''))

        session['dept_ids'] = request.values.getlist('dept_id')
        session['systems'] = request.values.getlist('system_id')
        session['dept_pros'] = request.values.getlist('dept_pro_id')
        session['duty_lv_ids'] = request.values.getlist('duty_lv_id')
        session['max_edu_level_ids'] = request.values.getlist('max_edu_level_id')
        session['at_edu_level_ids'] = request.values.getlist('at_edu_level_id')
        session['ot_edu_level_ids'] = request.values.getlist('ot_edu_level_id')
        session['state_ids'] = request.values.getlist('state_id')
        session['use_title_ids'] = request.values.getlist('use_title_id')
        session['title_dept_ids'] = request.values.getlist('title_dept_id')
        session['title_lv_ids'] = request.values.getlist('title_lv_id')

        session['work_time'] = str2time(form.get('work_time', ''))
        session['work_time_choice'] = form.get('work_time_choice', '')
        session['party_member'] = str2time(form.get('party_member', ''))
        session['party_member_choice'] = form.get('party_member_choice', '')
        session['val'] = None

    page = request.args.get('page', 1, type=int)
    dept_names = Dept.to_arr()
    duty_lvs = DutyLevel.to_array()
    all_fields = list(FIELDS.keys())
    fields = current_user.get_fields()
    query = Personnel.query.join(Duty)
    query = filter_query(query)
    pagination = query.order_by(Duty.order, Duty.duty_level_id.desc()) \
        .paginate(page, per_page=current_app.config['SEARCH_PAGE'],
                  error_out=False)
    pers = pagination.items
    pers = filter_field(pers, fields)
    return render_template('search.html', fields=fields, pers=pers,
                           all_fields=all_fields, pagination=pagination,
                           dept_names=dept_names, duty_lvs=duty_lvs,
                           endpoint='per.search_result',
                           export_api=url_for('v1.make_excel', val='is_none'))


def filter_query(query, is_none=True, is_all=False):
    """过滤查询"""
    min_age = session.get('min_age', 0)
    max_age = session.get('max_age', 0)
    re_name = session.get('re_name', '')
    re_sex = session.get('re_sex', '')
    re_phonetic = session.get('re_phonetic', '')
    re_nation = session.get('re_nation', '')
    re_id_card = session.get('re_id_card', '')
    re_cadre_id = session.get('re_cadre_id', '')
    dept_ids = session.get('dept_ids', '')
    systems = session.get('systems', '')
    dept_pros = session.get('dept_pros', '')
    duty_lv_ids = session.get('duty_lv_ids', '')
    max_edu_level_ids = session.get('max_edu_level_ids', '')
    at_edu_level_ids = session.get('at_edu_level_ids', '')
    ot_edu_level_ids = session.get('ot_edu_level_ids', '')
    work_time = session.get('work_time', '')
    work_time_choice = session.get('work_time_choice', '')
    party_member = session.get('party_member', '')
    party_member_choice = session.get('party_member_choice', '')
    re_policital_status = session.get('re_policital_status', '')
    re_native_place = session.get('re_native_place', '')
    re_birth_place = session.get('re_birth_place', '')
    re_identity = session.get('re_identity', '')
    re_work_no = session.get('re_work_no', '')
    re_work_year = session.get('re_work_year', '')
    state_ids = session.get('state_ids', '')
    use_title_ids = session.get('use_title_ids', '')
    title_dept_ids = session.get('title_dept_ids', '')
    title_lv_ids = session.get('title_lv_ids', '')
    re_major = session.get('re_major', '')
    re_duty = session.get('re_duty', '')
    val = session.get('val', '')

    # 筛选
    if val:
        query = query.filter(
            or_(
                Personnel.name.like('%' + val + '%'),
                Personnel.phonetic.like('%' + val + '%')
            )
        )
        return query

    if is_all:
        return query

    if re_name:
        is_none = False
        query = query.filter(Personnel.name.op('regexp')(re_name))

    if re_phonetic:
        is_none = False
        query = query.filter(Personnel.phonetic.op('regexp')(re_phonetic))

    if re_sex:
        is_none = False
        query = query.filter(Personnel.sex.op('regexp')(re_sex))

    if re_nation:
        is_none = False
        query = query.filter(Personnel.nation.op('regexp')(re_nation))

    if max_age and max_age != 0:
        is_none = False
        query = query.filter(Personnel.age.between(min_age, max_age))

    if re_id_card:
        is_none = False
        query = query.filter(Personnel.id_card.op('regexp')(re_id_card))

    if re_cadre_id:
        is_none = False
        query = query.filter(Personnel.cadre_id.op('regexp')(re_cadre_id))

    if dept_ids or systems or dept_pros:
        is_none = False
        query = query.join(Dept)
        if dept_ids:
            query = query.filter(Dept.id.in_(dept_ids))
        if systems:
            query = query.filter(Dept.system_id.in_(systems))
        if dept_pros:
            query = query.filter(Dept.dept_pro_id.in_(dept_pros))

    if duty_lv_ids:
        is_none = False
        query = query.filter(Duty.duty_level_id.in_(duty_lv_ids))

    if max_edu_level_ids or at_edu_level_ids or ot_edu_level_ids:
        is_none = False
        query = query.join(Education)
        if max_edu_level_ids:
            query = query.filter(Personnel.max_edu_id.in_(max_edu_level_ids))
        if at_edu_level_ids:
            query = query.filter(Personnel.at_edu_id.in_(at_edu_level_ids))
        if ot_edu_level_ids:
            query = query.filter(Personnel.ot_edu_id.in_(ot_edu_level_ids))

    if work_time and work_time_choice:
        is_none = False
        if work_time_choice == ">":
            query = query.filter(Personnel.work_time > work_time)
        elif work_time_choice == "<":
            query = query.filter(Personnel.work_time < work_time)

    if party_member and party_member_choice:
        is_none = False
        if party_member_choice == ">":
            query = query.filter(Personnel.party_member > party_member)
        elif party_member_choice == "<":
            query = query.filter(Personnel.party_member < party_member)

    if re_policital_status:
        is_none = False
        query = query.filter(
            Personnel.policital_status.op('regexp')(re_policital_status)
        )

    if re_native_place:
        is_none = False
        query = query.filter(Personnel.native_place.op('regexp')(re_native_place))

    if re_birth_place:
        is_none = False
        query = query.filter(Personnel.birth_place.op('regexp')(re_birth_place))

    if re_identity:
        is_none = False
        query = query.filter(Personnel.identity.op('regexp')(re_identity))

    if re_work_no:
        is_none = False
        query = query.filter(Personnel.work_no.op('regexp')(re_work_no))

    if re_work_year:
        is_none = False
        query = query.filter(Personnel.s_work_year.op('regexp')(re_work_year))

    if state_ids:
        is_none = False
        query = query.filter(Personnel.state_id.in_(state_ids))

    if use_title_ids:
        is_none = False
        query = query.filter(Personnel.use_title_name_id.in_(use_title_ids))

    if title_dept_ids or title_lv_ids:
        is_none = False
        query = query.join(TitleName,
                           TitleName.id == Personnel.use_title_name_id)
        if title_dept_ids:
            query = query.filter(TitleName.title_dept_id.in_(title_dept_ids))
        if title_lv_ids:
            query = query.filter(TitleName.title_lv_id.in_(title_lv_ids))

    if re_major:
        is_none = False
        query = query.join(Title, Title.id == Personnel.use_title_id)
        query = query.filter(Title.major.op('regexp')(re_major))

    if re_duty:
        is_none = False
        query = query.filter(Duty.name.op('regexp')(re_duty))

    if is_none:
        query = query.filter(Personnel.id < 0)

    return query
