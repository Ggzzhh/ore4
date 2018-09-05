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
    # 单位简称
    dept_name = db.Column(db.String(64))
    # 单位全称
    full_name = db.Column(db.String(256))
    # 支部名称
    branch_name = db.Column(db.String(128))
    # 级别编号
    order = db.Column(db.Integer, default=10)
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
            dept = Dept.query.get_or_404(data.get('id'))
            add = False
        else:
            dept = ''
            add = ''
            abort(403)
        system = System.query.get(data.get('system_id'))
        dept_pro = DeptPro.query.get(data.get('dept_pro_id'))
        print(dept_pro)
        dept.system = system
        dept.dept_pro = dept_pro
        dept.order = data.get('order')
        return dept, add

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.dept_name,
            'order': self.order,
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
    # 姓名
    name = db.Column(db.String(16), nullable=False)
    # 拼音简称
    phonetic = db.Column(db.String(16))
    # 性别
    sex = db.Column(db.String(2))
    # 民族
    nation = db.Column(db.String(32))
    # 生日
    birthday = db.Column(db.DateTime)
    # 干部编号
    cadre_id = db.Column(db.String(64))
    # 身份证
    id_card = db.Column(db.String(128))
    # 参加工作时间
    work_time = db.Column(db.DateTime)
    # 入党时间
    party_member = db.Column(db.DateTime)
    # 籍贯
    native_place = db.Column(db.String(32))
    # 出生地
    birth_place = db.Column(db.String(32))
    # 专长
    specialty = db.Column(db.String(64))
    # 任副科级时间
    deputy_sc_time = db.Column(db.DateTime)
    # 任正科级时间
    sc_time = db.Column(db.DateTime)
    # 任现职时间
    position_time = db.Column(db.DateTime)
    # 任副总时间
    VGM_time = db.Column(db.DateTime)
    # 任代理时间
    agent_time = db.Column(db.DateTime)
    # 身份
    identity = db.Column(db.DateTime)
    # 工号
    work_no = db.Column(db.Integer)
    # 特殊工作年限
    s_work_year = db.Column(db.String(16))
    # 荣誉金
    bonus = db.Column(db.String(128))
    # 档案备注
    remarks = db.Column(db.Text)
    # 调入备注
    remarks_2 = db.Column(db.Text)
    # 受处分
    punished = db.Column(db.Boolean)
    # 照片地址
    photo_src = db.Column(db.String(128))
    # 家庭情况
    families = db.relationship('Family', backref='personnel', lazy='dynamic')
    # 奖惩情况
    r_and_p = db.relationship('RAndP', backref='personnel', lazy='dynamic')
    # 学历
    edus = db.relationship('Education', backref='personnel', lazy='joined')
    # 简历
    resumes = db.relationship('Resume', backref='personnel', lazy='joined')
    # 职称
    titlies = db.relationship('Title', backref='personnel', lazy='joined')
    # 职务
    duty_id = db.Column(db.Integer, db.ForeignKey('duties.id'))
    # 单位
    dept_id = db.Column(db.Integer, db.ForeignKey('depts.id'))
    # 状态
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
    # 变动时间
    change_time = db.Column(db.DateTime)
    # 任职时间
    work_time = db.Column(db.DateTime)
    # 职务
    duty = db.Column(db.String(64))
    # 任职文号
    identifier = db.Column(db.String(64))

    def __repr__(self):
        return "<{}的简历>".format(self.personnel.name)


class RAndP(db.Model):
    """奖惩 英文：rewards and penalties 缩写为RAndP"""
    __tablename__ = 'r_and_p'
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    # 时间
    time = db.Column(db.DateTime)
    # 奖惩单位
    dept = db.Column(db.String(64))
    # 奖惩原因
    reason = db.Column(db.String(128))
    # 奖惩结果
    result = db.Column(db.String(128))
    # 备注
    remarks = db.Column(db.String(200))

    def __repr__(self):
        return "<奖惩结果: {}>".format(self.result)


class Education(db.Model):
    __tablename__ = 'education'
    id = db.Column(db.Integer, primary_key=True)
    # 学历
    edu_level_id = db.Column(db.Integer, db.ForeignKey('edu_levels.id'))
    # 所属人
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    # 入学时间
    enrolment_time = db.Column(db.DateTime)
    # 毕业时间
    graduation_time = db.Column(db.DateTime)
    # 学校名
    edu_name = db.Column(db.String(128))
    # 专业名
    department = db.Column(db.String(64))
    # 学位
    degree = db.Column(db.String(64))
    # 学习形式
    learn_id = db.Column(db.Integer, db.ForeignKey('learn_forms.id'))
    # 备注
    remarks = db.Column(db.String(300))

    def __repr__(self):
        return "<学校名: {}>".format(self.edu_name)


class EduLevel(db.Model):
    __tablename__ = 'edu_levels'
    id = db.Column(db.Integer, primary_key=True)
    edu = db.relationship('Education', backref='edu_level',
                               lazy='joined')
    # 排序用 筛选最高学历时使用
    value = db.Column(db.Integer)
    level = db.Column(db.String(32))

    def __repr__(self):
        return "<学历: {}>".format(self.level)


class LearnForm(db.Model):
    __tablename__ = 'learn_forms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    edu = db.relationship('Education', backref='learn_form', lazy='joined')

    def __repr__(self):
        return "<学习形式: {}>".format(self.name)


class Family(db.Model):
    __tablename__ = 'families'
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    # 称谓
    relationship = db.Column(db.String(16))
    # 姓名
    name = db.Column(db.String(16))
    # 年龄
    age = db.Column(db.Integer)
    # 政治面貌  political climate
    p_c = db.Column(db.String(16))
    # 工作地点
    workplace = db.Column(db.String(64))

    def __repr__(self):
        return "<家人姓名: {}>".format(self.name)


class Duty(db.Model):
    __tablename__ = 'duties'
    id = db.Column(db.Integer, primary_key=True)
    personnels = db.relationship('Personnel', backref='duty', lazy='dynamic')
    name = db.Column(db.String(32))
    order = db.Column(db.Integer, default=10)
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
    # 职称名
    name_id = db.Column(db.Integer, db.ForeignKey('title_names.id'))
    # 归属人
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnels.id'))
    # 职称专业
    major = db.Column(db.String(32))
    # 取得时间
    get_time = db.Column(db.DateTime)
    # 备注
    remarks = db.Column(db.String(300))
    # 证书编号
    page_no = db.Column(db.String(128))
    # 是否在聘
    engage = db.Column(db.Boolean, default=False)
    # 聘任时间
    engage_time = db.Column(db.DateTime)

    def __repr__(self):
        return "<职称: {}>".format(self.name)


class TitleName(db.Model):
    __tablename__ = 'title_names'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    titles = db.relationship('Title', backref='name', lazy='dynamic')
    title_lv_id = db.Column(db.Integer, db.ForeignKey('title_lv.id'))
    title_dept_id = db.Column(db.Integer, db.ForeignKey('title_dept.id'))


class TitleDept(db.Model):
    __tablename__ = 'title_dept'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    titlies = db.relationship('TitleName', backref='dept', lazy='dynamic')

    def __repr__(self):
        return "<职称系列: {}>".format(self.name)


class TitleLv(db.Model):
    __tablename__ = 'title_lv'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    titlies = db.relationship('TitleName', backref='lv', lazy='dynamic')

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