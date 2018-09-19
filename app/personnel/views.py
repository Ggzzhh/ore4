# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, flash, session
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel
from sqlalchemy import text, or_

from . import per
from ..const import FIELDS
from ..tools import filter_field
from ..models import EduLevel, LearnForm, TitleName, DeptPro, \
    Dept, DutyLevel, State, Personnel, Nation, System, Duty


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
    return render_template('search/condition.html', systems=systems,
                           nations=nations, pros=pros, lvs=lvs,
                           edu_lvs=edu_lvs, states=states)


@per.route('/search-result',  methods=["POST", "GET"])
@login_required
def search_result():
    if request.method == "POST":
        form = request.form
        print(form)

        # 年龄相关
        max_age = 0
        min_age = -1
        try:
            age1 = int(form.get('age1', 0))
            age2 = int(form.get('age2', 0))
            min_age = min([age1, age2])
            max_age = max([age1, age2])
            session['min_age'] = min_age
            session['max_age'] = max_age
        except:
            pass

        re_name = r'{}'.format(form.get('name', ''))
        re_phonetic = r'{}'.format(form.get('phonetic', ''))
        re_sex = r'{}'.format(form.get('sex', ''))
        re_nation = r'{}'.format(form.get('nation', ''))
        re_id_card = r'{}'.format(form.get('id_card', ''))
        re_cadre_id = r'{}'.format(form.get('cadre_id', ''))

        # 单位相关
        dept_ids = request.values.getlist('dept_id')
        print(dept_ids)

        session['re_name'] = re_name
        session['re_phonetic'] = re_phonetic
        session['re_sex'] = re_sex
        session['re_nation'] = re_nation
        session['re_id_card'] = re_id_card
        session['re_cadre_id'] = re_cadre_id
    else:
        min_age = session.get('min_age', 0)
        max_age = session.get('max_age', 0)
        re_name = session.get('re_name', '')
        re_sex = session.get('re_sex', '')
        re_phonetic = session.get('re_phonetic', '')
        re_nation = session.get('re_nation', '')
        re_id_card = session.get('re_id_card', '')
        re_cadre_id = session.get('re_cadre_id', '')

    page = request.args.get('page', 1, type=int)
    dept_names = Dept.to_arr()
    duty_lvs = DutyLevel.to_array()
    all_fields = list(FIELDS.keys())
    fields = current_user.get_fields()
    query = Personnel.query.join(Duty)

    # 筛选
    if re_name:
        query = query.filter(Personnel.name.op('regexp')(re_name))
    if re_phonetic:
        query = query.filter(Personnel.phonetic.op('regexp')(re_phonetic))
    if re_sex:
        query = query.filter(Personnel.sex.op('regexp')(re_sex))
    if re_nation:
        query = query.filter(Personnel.nation.op('regexp')(re_nation))
    if max_age and max_age != 0:
        query = query.filter(Personnel.age.between(min_age, max_age))
    if re_id_card:
        query = query.filter(Personnel.id_card.op('regexp')(re_id_card))
    if re_cadre_id:
        query = query.filter(Personnel.cadre_id.op('regexp')(re_cadre_id))

    pagination = query.order_by(Duty.order, Duty.duty_level_id.desc()) \
        .paginate(page, per_page=current_app.config['PER_PAGE'],
                  error_out=False)
    pers = pagination.items
    pers = filter_field(pers, fields)
    return render_template('search.html', fields=fields, pers=pers,
                           all_fields=all_fields, pagination=pagination,
                           dept_names=dept_names, duty_lvs=duty_lvs)
