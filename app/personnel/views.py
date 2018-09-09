# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify, \
    current_app, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user
import flask_excel as excel

from . import per
from ..models import EduLevel, LearnForm, TitleName, Dept, DutyLevel


@per.route('/add')
@login_required
def add_per():
    edu_lv = EduLevel.to_arr()
    learn_form = LearnForm.to_arr()
    title_names = TitleName.to_arr()
    dept_names = Dept.to_arr()
    duty_lvs = DutyLevel.to_array()
    return render_template('per/add.html', title='新增人员', edu_lv=edu_lv,
                           learn_form=learn_form, title_names=title_names,
                           dept_names=dept_names, duty_lvs=duty_lvs)