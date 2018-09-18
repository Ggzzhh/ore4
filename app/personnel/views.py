# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel

from . import per
from ..models import EduLevel, LearnForm, TitleName, DeptPro,\
    Dept, DutyLevel, State, Personnel, Nation, System


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


@per.route('/condition-search', methods=["GET", "POST"])
@login_required
def condition_search():
    systems = System.query.order_by('id').all()
    nations = Nation.to_arr()
    pros = DeptPro.to_array()
    lvs = DutyLevel.to_array()
    edu_lvs = EduLevel.to_arr()
    states = State.to_arr()
    if request.method == "POST":
        print(request.form)
    return render_template('search/condition.html', systems=systems,
                           nations=nations, pros=pros, lvs=lvs,
                           edu_lvs=edu_lvs, states=states)