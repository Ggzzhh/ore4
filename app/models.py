# -*- coding: utf-8 -*-
import html
import hashlib
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    if user_id:
        user = User.query.get(int(user_id))
        return user
    return None


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<角色: %r>' % self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    retry_count = db.Column(db.Integer, default=10)
    disable_time = db.Column(db.DateTime)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.role:
            self.role = Role.query.filter_by(name='user').first()

    @property
    def password(self):
        raise AttributeError("这不是一个可读属性")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role.name == 'admin'

    def __repr__(self):
        return '<用户名: %r>-%r' % (self.username, self.role)


class System(db.Model):
    __tablename__ = 'systems'
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(64), unique=True)
    depts = db.relationship('Dept', backref='system')


class Dept(db.Model):
    __tablename__ = 'depts'
    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(64), unique=True)
    personnels = db.relationship('Personnel', backref='duty')
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id'))
    dept_pro_id = db.Column(db.Integer, db.ForeignKey('dept_pros.id'))


class DeptPro(db.Model):
    __tablename__ = 'dept_pros'
    id = db.Column(db.Integer, primary_key=True)
    dept_pro_name = db.Column(db.String(64), unique=True)
    depts = db.relationship('Dept', backref='dept_pro')


class Personnel(db.Model):
    __tablename__ = 'personnels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    sex = db.Column(db.String(2))
    nation = db.Column(db.String(32))
    birthday = db.Column(db.DateTime)
    cadre_id = db.Column(db.Integer)
    id_card = db.Column(db.Integer)
    work_time = db.Column(db.DateTime)
    party_member = db.Column(db.DateTime)
    native_place = db.Column(db.String(32))
    birth_place = db.Column(db.String(32))
    specialty = db.Column(db.String(64))
    deputy_sc_time = db.Column(db.DateTime)
    sc_time = db.Column(db.DateTime)
    position_time = db.Column(db.DateTime)
    identity = db.Column(db.DateTime)
    work_no = db.Column(db.Integer)
    work_year = db.Column(db.String(16))
    bonus = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    remarks_2 = db.Column(db.Text)
    families = db.relationship('Family', backref='personnel')
    r_and_p = db.relationship('RAndP', backref='personnel')
    f_t_edu = db.relationship('FullTimeEdu', backref='personnel')
    i_s_edu = db.relationship('InServiceEdu', backref='personnel')
    resumes = db.relationship('Resume', backref='personnel')
    duty_id = db.Column(db.Integer, db.ForeignKey('duties.id'))
    title_id = db.Column(db.Integer, db.ForeignKey('titlies.id'))
    dept_id = db.Column(db.Integer, db.ForeignKey('depts.id'))
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'))


class Resume(db.Model):
    __tablename__ = 'resumes'
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    work_time = db.Column(db.DateTime)
    duty = db.Column(db.String(64))
    duty_lv = db.Column(db.String(64))
    identifier = db.Column(db.String(64))


class RAndP(db.Model):
    """奖惩 英文：rewards and penalties 缩写为RAndP"""
    __tablename__ = 'r_and_p'
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    content = db.Column(db.String(200))


class FullTimeEdu(db.Model):
    __tablename__ = 'full_time_edus'
    id = db.Column(db.Integer, primary_key=True)
    edu_level_id = db.Column(db.Integer, db.ForeignKey('edu_levels.id'))
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    enrolment_time = db.Column(db.DateTime)
    graduation_time = db.Column(db.DateTime)
    edu = db.Column(db.String(64))
    department = db.Column(db.String(64))


class InServiceEdu(db.Model):
    __tablename__ = 'in_service_edus'
    id = db.Column(db.Integer, primary_key=True)
    edu_level_id = db.Column(db.Integer, db.ForeignKey('edu_levels.id'))
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    enrolment_time = db.Column(db.DateTime)
    graduation_time = db.Column(db.DateTime)
    edu = db.Column(db.String(64))
    department = db.Column(db.String(64))


class EduLevel(db.Model):
    __tablename__ = 'edu_levels'
    id = db.Column(db.Integer, primary_key=True)
    i_s_edu = db.relationship('InServiceEdu', backref='edu_level', uselist=False)
    f_t_edu = db.relationship('FullTimeEdu', backref='edu_level', uselist=False)
    value = db.Column(db.Integer)
    level = db.Column(db.String(32))


class Family(db.Model):
    __tablename__ = 'families'
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    relationship = db.Column(db.String(16))
    name = db.Column(db.String(16))
    age = db.Column(db.Integer)
    # 政治面貌  political climate
    p_c = db.Column(db.String(16))
    workplace = db.Column(db.String(64))


class Duty(db.Model):
    __tablename__ = 'duties'
    id = db.Column(db.Integer, primary_key=True)
    personnels = db.relationship('Personnel', backref='duty')
    name = db.Column(db.String(32))
    duty_level_id = db.Column(db.Integer, db.ForeignKey('duty_level.id'))


class DutyLevel(db.Model):
    __tablename__ = 'duty_level'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    duties = db.relationship('Duty', backref='duty_level')


class Title(db.Model):
    __tablename__ = 'titlies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    personnels = db.relationship('Personnel', backref='title')
    title_lv_id = db.Column(db.Integer, db.ForeignKey('title_lv.id'))
    title_dept_id = db.Column(db.Integer, db.ForeignKey('title_dept.id'))


class TitleDept(db.Model):
    __tablename__ = 'title_dept'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    titlies = db.relationship('Title', backref='title_dept')


class TitleLv(db.Model):
    __tablename__ = 'title_lv'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    titlies = db.relationship('Title', backref='title_lv')


class State(db.Model):
    __tablename__ = 'states'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    personnels = db.relationship('Personnel', backref='state')


def run_only():

    def register_role():
        db.drop_all()
        db.create_all()
        admin = Role(name='admin')
        leader = Role(name='leader')
        cadre = Role(name='cadre')
        staff = Role(name='staff')
        db.session.add(admin)
        db.session.add(leader)
        db.session.add(cadre)
        db.session.add(staff)
        db.session.commit()

    def register_admin():
        only_admin = User(username=current_app.config['ADMIN_USERNAME'])
        only_admin.password = current_app.config['ADMIN_PASSWORD']
        only_admin.role = Role.query.filter_by(name='admin').first()
        print(only_admin)
        db.session.add(only_admin)
        db.session.commit()

    register_role()
    register_admin()
    print('ok')