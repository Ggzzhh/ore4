# -*- coding: utf-8 -*-
from datetime import datetime, date

from flask import current_app, abort
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    if user_id:
        user = User.query.get(int(user_id))
        return user
    return None


class Per2Title(db.Model):
    __tablename__ = 'follows'
    date = db.Column('date', db.DateTime, default=date.today())
    per_id = db.Column(db.Integer, db.ForeignKey('personnels.id'), primary_key=True)
    title_id = db.Column( db.Integer, db.ForeignKey('titlies.id'), primary_key=True)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

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
    depts = db.relationship('Dept', backref='system', lazy='dynamic')

    @staticmethod
    def to_array():
        data = System.query.order_by('id').all()
        return [[s.id, s.system_name] for s in data]

    def __repr__(self):
        return '<单位系统: %r>' % self.system_name


class Dept(db.Model):
    __tablename__ = 'depts'
    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(64), unique=True)
    personnels = db.relationship('Personnel', backref='dept', lazy='dynamic')
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id'))
    dept_pro_id = db.Column(db.Integer, db.ForeignKey('dept_pros.id'))

    @staticmethod
    def from_json(data):
        new = data.get('new')
        if new is True:
            dept = Dept(dept_name=data.get('name'))
            if dept.dept_name is None:
                return None, True
            add = True
        elif new is False:
            dept = Dept.query.get_or_404(id)
            add = False
        else:
            dept = ''
            add = ''
            abort(403)
        dept.system_id = data.get('system_id')
        dept.dept_pro_id = data.get('dept_pro_id')
        return dept, add

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.dept_name,
            'system_id': self.system_id,
            'system': self.system.system_name if self.system is not None
            else '',
            'dept_pro_id': self.dept_pro_id,
            'dept_pro': self.dept_pro.dept_pro_name if self.dept_pro is not None
            else ''
        }
        return data

    def __repr__(self):
        return '<单位: %r>' % self.dept_name


class DeptPro(db.Model):
    __tablename__ = 'dept_pros'
    id = db.Column(db.Integer, primary_key=True)
    dept_pro_name = db.Column(db.String(64), unique=True)
    depts = db.relationship('Dept', backref='dept_pro', lazy='dynamic')

    @staticmethod
    def to_array():
        pros = DeptPro.query.order_by('id').all()
        return [[p.id, p.dept_pro_name] for p in pros]

    def __repr__(self):
        return '<单位属性: %r>' % self.dept_pro_name


class Personnel(db.Model):
    __tablename__ = 'personnels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    phonetic = db.Column(db.String(16))
    sex = db.Column(db.String(2))
    nation = db.Column(db.String(32))
    birthday = db.Column(db.DateTime)
    cadre_id = db.Column(db.String(64))
    id_card = db.Column(db.String(128))
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
    punished = db.Column(db.Boolean)
    families = db.relationship('Family', backref='personnel', lazy='dynamic')
    r_and_p = db.relationship('RAndP', backref='personnel', lazy='dynamic')
    f_t_edu = db.relationship('FullTimeEdu', backref='personnel', lazy='dynamic')
    i_s_edu = db.relationship('InServiceEdu', backref='personnel', lazy='dynamic')
    resumes = db.relationship('Resume', backref='personnel', lazy='dynamic')
    titlies = db.relationship('Per2Title', foreign_keys=[Per2Title.per_id],
                              backref=db.backref('personnel', lazy='joined'),
                              lazy='dynamic', cascade='all, delete-orphan')
    duty_id = db.Column(db.Integer, db.ForeignKey('duties.id'))
    dept_id = db.Column(db.Integer, db.ForeignKey('depts.id'))
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'))

    def top_title(self):
        l = self.titlies.order_by(Per2Title.date.desc()).all()
        return l[0].title if l else None

    @property
    def system(self):
        return self.duty.system.system_name

    def __repr__(self):
        return "<员工姓名: {}>".format(self.name)


class Resume(db.Model):
    __tablename__ = 'resumes'
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    work_time = db.Column(db.DateTime)
    duty = db.Column(db.String(64))
    duty_lv = db.Column(db.String(64))
    identifier = db.Column(db.String(64))

    def __repr__(self):
        return "<{}的简历>".format(self.personnel.name)


class RAndP(db.Model):
    """奖惩 英文：rewards and penalties 缩写为RAndP"""
    __tablename__ = 'r_and_p'
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    content = db.Column(db.String(200))

    def __repr__(self):
        return "<奖惩内容: {}>".format(self.content)


class FullTimeEdu(db.Model):
    __tablename__ = 'full_time_edus'
    id = db.Column(db.Integer, primary_key=True)
    edu_level_id = db.Column(db.Integer, db.ForeignKey('edu_levels.id'))
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    enrolment_time = db.Column(db.DateTime)
    graduation_time = db.Column(db.DateTime)
    edu = db.Column(db.String(64))
    department = db.Column(db.String(64))

    def __repr__(self):
        return "<全日制学历: {}>".format(self.edu)


class InServiceEdu(db.Model):
    __tablename__ = 'in_service_edus'
    id = db.Column(db.Integer, primary_key=True)
    edu_level_id = db.Column(db.Integer, db.ForeignKey('edu_levels.id'))
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    enrolment_time = db.Column(db.DateTime)
    graduation_time = db.Column(db.DateTime)
    edu = db.Column(db.String(64))
    department = db.Column(db.String(64))

    def __repr__(self):
        return "<在职学历: {}>".format(self.edu)


class EduLevel(db.Model):
    __tablename__ = 'edu_levels'
    id = db.Column(db.Integer, primary_key=True)
    i_s_edus = db.relationship('InServiceEdu', backref='edu_level',
                               lazy='dynamic')
    f_t_edus = db.relationship('FullTimeEdu', backref='edu_level',
                               lazy='dynamic')
    value = db.Column(db.Integer)
    level = db.Column(db.String(32))

    def __repr__(self):
        return "<学历等级: {}>".format(self.level)


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

    def __repr__(self):
        return "<家人姓名: {}>".format(self.name)


class Duty(db.Model):
    __tablename__ = 'duties'
    id = db.Column(db.Integer, primary_key=True)
    personnels = db.relationship('Personnel', backref='duty', lazy='dynamic')
    name = db.Column(db.String(32))
    order = db.Column(db.Integer, default=1)
    duty_level_id = db.Column(db.Integer, db.ForeignKey('duty_level.id'))

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.name,
            'order': self.order,
            'duty_level_id': self.duty_level_id,
            'duty_level': self.duty_level.name if self.duty_level is not None
            else ''
        }
        return data

    @staticmethod
    def from_json(data):
        if data is None or data.get('name') is None:
            abort(403)
        _id = data.get('id')
        name = data.get('name')
        duty_level_id = data.get('duty_level_id')
        if _id is not None:
            temp = Duty.query.get_or_404(_id)
        else:
            temp = Duty()
        temp.name = name
        temp.duty_level_id = duty_level_id
        return temp

    def __repr__(self):
        return "<职务: {}>".format(self.name)


class DutyLevel(db.Model):
    __tablename__ = 'duty_level'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    value = db.Column(db.Integer, default=0)
    duties = db.relationship('Duty', backref='duty_level', lazy='dynamic')

    @staticmethod
    def to_array():
        duty_lvs = DutyLevel.query.all()
        return [[l.id, l.name] for l in duty_lvs]

    def __repr__(self):
        return "<职务等级: {}>".format(self.name)


class Title(db.Model):
    __tablename__ = 'titlies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    personnels = db.relationship('Per2Title', foreign_keys=[Per2Title.title_id],
                              backref=db.backref('title', lazy='joined'),
                              lazy='dynamic', cascade='all, delete-orphan')
    title_lv_id = db.Column(db.Integer, db.ForeignKey('title_lv.id'))
    title_dept_id = db.Column(db.Integer, db.ForeignKey('title_dept.id'))

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.name,
            'title_lv_id': self.title_lv_id,
            'title_dept_id': self.title_dept_id,
            'title_lv': self.title_lv.name if self.title_lv is not None else '',
            'title_dept': self.title_dept.name
            if self.title_dept is not None else '',
        }
        return data

    @staticmethod
    def from_json(data):
        if data is None or data.get('name') is None:
            abort(403)
        _id = data.get('id')
        name = data.get('name')
        title_lv_id = data.get('title_lv_id')
        title_dept_id = data.get('title_dept_id')
        if _id is not None:
            temp = Title.query.get_or_404(_id)
        else:
            temp = Title()
        temp.name = name
        temp.title_lv_id = title_lv_id
        temp.title_dept_id = title_dept_id
        return temp

    def __repr__(self):
        return "<职称: {}>".format(self.name)


class TitleDept(db.Model):
    __tablename__ = 'title_dept'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    titlies = db.relationship('Title', backref='title_dept', lazy='dynamic')

    def __repr__(self):
        return "<职称系列: {}>".format(self.name)


class TitleLv(db.Model):
    __tablename__ = 'title_lv'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    titlies = db.relationship('Title', backref='title_lv', lazy='dynamic')

    def __repr__(self):
        return "<职称等级: {}>".format(self.name)


class State(db.Model):
    __tablename__ = 'states'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    personnels = db.relationship('Personnel', backref='state', lazy='dynamic')

    def __repr__(self):
        return "<状态: {}>".format(self.name)


def run_only():

    def register_role():
        admin = Role(name='管理员', id=1)
        leader = Role(name='审查者')
        db.session.add(admin)
        db.session.add(leader)
        db.session.commit()

    def register_admin():
        only_admin = User(username=current_app.config['ADMIN_USERNAME'])
        only_admin.password = current_app.config['ADMIN_PASSWORD']
        only_admin.role = Role.query.get(1)
        print(only_admin)
        db.session.add(only_admin)
        db.session.commit()

    register_role()
    register_admin()
    print('ok')