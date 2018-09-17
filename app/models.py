# -*- coding: utf-8 -*-
from datetime import datetime, date

from flask import current_app, abort
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager
from .tools import str2time, str2img, calculate_age, time2str, str2pinyin


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
    fields = ",".join(["在职：管理人员", "在职：专技人员", "在职：一般管理人员",
                       "协理", "调离", "退休", "去世"])
    fields = db.Column(db.String(512), default=fields)

    def get_fields(self):
        if self.fields:
            fields = self.fields.split(",")
            return fields
        else:
            return []

    def set_fields(self, L):
        self.fields = ",".join(L)
        return self

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
    full_name = db.Column(db.String(256), default='')
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
        dept.system = system
        dept.dept_pro = dept_pro
        dept.order = data.get('order')
        dept.full_name = data.get('full_name')
        return dept, add

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.dept_name,
            'full_name': self.full_name,
            'order': self.order,
            'system_id': self.system_id,
            'system': self.system.system_name if self.system is not None
            else '',
            'dept_pro_id': self.dept_pro_id,
            'dept_pro': self.dept_pro.dept_pro_name if self.dept_pro is not None
            else ''
        }
        return data

    @staticmethod
    def to_arr():
        names = []
        for dept in Dept.query.all():
            names.append([dept.id, dept.dept_name, dept.system.system_name,
                          dept.dept_pro.dept_pro_name])
        return names

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
    sex = db.Column(db.String(4))
    # 民族
    nation = db.Column(db.String(32))
    # 生日
    birthday = db.Column(db.DateTime)
    # 干部编号
    cadre_id = db.Column(db.String(64))
    # 身份证
    id_card = db.Column(db.String(128), unique=True)
    # 参加工作时间
    work_time = db.Column(db.DateTime)
    # 入党时间
    party_member = db.Column(db.DateTime)
    # policital status 政治面貌
    policital_status = db.Column(db.String(16))
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
    identity = db.Column(db.String(16))
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
    punished = db.Column(db.Boolean, default=False)
    # 照片地址
    photo_src = db.Column(db.String(128))
    # 家庭情况
    families = db.relationship('Family', backref='personnel', lazy='joined')
    # 奖惩情况
    r_and_ps = db.relationship('RAndP', backref='personnel', lazy='joined')
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

    @staticmethod
    def from_json(data, id=None):
        if id is not None:
            per = Personnel.query.get_or_404(id)
        else:
            per = Personnel(name=data.get('name'))
        per.phonetic = str2pinyin(per.name)
        per.cadre_id = data.get('cadre_id')
        per.sex = data.get('sex')
        per.nation = data.get('nation')
        per.specialty = data.get('specialty')
        photo_src = "/static/image/timg.jpg"
        src = data.get('photo_src')
        if src:
            if src != photo_src:
                if src[-4:] != '.jpg':
                    src = src[23:]
                photo_src = str2img(src, "/static/per_img/", data.get(
                    'id_card'))
        per.photo_src = photo_src
        per.id_card = data.get('id_card')
        per.birthday = str2time(data.get('birthday'))
        per.age = data.get('age')
        per.policital_status = data.get('policital_status')
        per.identity = data.get('identity')
        per.party_member = str2time(data.get('party_member'))
        per.work_time = str2time(data.get('work_time'))
        per.native_place = data.get('native_place')
        per.birth_place = data.get('birth_place')
        if data.get('work_no'):
            per.work_no = int(data.get('work_no'))
        per.s_work_year = data.get('s_work_year')
        per.bonus = data.get('bonus')
        per.remarks = data.get('remarks')
        per.remarks_2 = data.get('remarks_2')
        per.deputy_sc_time = str2time(data.get('deputy_sc_time'))
        per.sc_time = str2time(data.get('sc_time'))
        per.position_time = str2time(data.get('position_time'))
        per.VGM_time = str2time(data.get('VGM_time'))
        per.agent_time = str2time(data.get('agent_time'))
        return per

    def to_json(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['phonetic'] = self.phonetic
        data['sex'] = self.sex
        data['nation'] = self.nation
        data['birthday'] = time2str(self.birthday)
        data['age'] = calculate_age(self.birthday)
        data['cadre_id'] = self.cadre_id
        data['id_card'] = self.id_card
        data['work_time'] = time2str(self.work_time)
        data['party_member'] = time2str(self.party_member)
        data['policital_status'] = self.policital_status
        data['native_place'] = self.native_place
        data['birth_place'] = self.birth_place
        data['specialty'] = self.specialty
        data['deputy_sc_time'] = time2str(self.deputy_sc_time)
        data['sc_time'] = time2str(self.sc_time)
        data['position_time'] = time2str(self.position_time)
        data['VGM_time'] = time2str(self.VGM_time)
        data['agent_time'] = time2str(self.agent_time)
        data['identity'] = self.identity
        data['work_no'] = self.work_no
        data['s_work_year'] = self.s_work_year
        data['bonus'] = self.bonus
        data['remarks'] = self.remarks
        data['remarks_2'] = self.remarks_2
        data['punished'] = '是' if self.punished else '否'
        data['photo_src'] = self.photo_src
        data['families'] = self.families
        data['r_and_ps'] = self.r_and_ps
        data['resumes'] = self.resumes
        data['titlies'] = self.titlies
        data['title_name'] = self.title
        if self.duty:
            duty = self.duty.to_json()
            data['duty'] = duty
            data['duty_name'] = duty['name']
            data['duty_lv'] = duty['duty_level']
            data['duty_level_id'] = duty['duty_level_id']
        if self.dept:
            dept = self.dept.to_json()
            data['dept'] = dept
            data['dept_name'] = dept['name']
            data['system'] = dept['system']
            data['dept_pro'] = dept['dept_pro']
        if self.state:
            data['state_id'] = self.state_id
            data['state'] = self.state.name
        data['edus'] = self.edus
        if self.max_edu:
            data['max_edu'] = self.max_edu
            data['max_edu_lv'] = self.max_edu.edu_level.level
            data['max_edu_in_time'] = time2str(self.max_edu.enrolment_time)
            data['max_edu_time'] = time2str(self.max_edu.graduation_time)
            data['max_edu_dept'] = self.max_edu.department
            data['max_edu_name'] = self.max_edu.edu_name
            data['max_edu_learn_form'] = self.max_edu.learn_form.name
        if self.at_edu:
            data['at_edu'] = self.at_edu
            data['at_edu_lv'] = self.at_edu.edu_level.level
            data['at_edu_time'] = time2str(self.at_edu.graduation_time)
            data['at_edu_in_time'] = time2str(self.at_edu.enrolment_time)
            data['at_edu_name'] = self.at_edu.edu_name
            data['at_edu_dept'] = self.at_edu.department
            data['at_edu_learn_form'] = self.at_edu.learn_form.name
        if self.ot_edu:
            data['ot_edu'] = self.ot_edu
            data['ot_edu_lv'] = self.ot_edu.edu_level.level
            data['ot_edu_time'] = time2str(self.ot_edu.graduation_time)
            data['ot_edu_in_time'] = time2str(self.ot_edu.enrolment_time)
            data['ot_edu_name'] = self.ot_edu.edu_name
            data['ot_edu_dept'] = self.ot_edu.department
            data['ot_edu_learn_form'] = self.ot_edu.learn_form.name
        return data

    @property
    def title(self):
        if self.titlies:
            return self.titlies[-1].name.name
        return

    @property
    def max_edu(self):
        return self.max_edus(self.edus)

    @property
    def at_edu(self):
        L = []
        for edu in self.edus:
            if edu.learn_form:
                if edu.learn_form.id == 1:
                    L.append(edu)
        return self.max_edus(L)

    @property
    def ot_edu(self):
        L = []
        for edu in self.edus:
            if edu.learn_form:
                if edu.learn_form.id != 1:
                    L.append(edu)
        return self.max_edus(L)

    @staticmethod
    def max_edus(edus):
        temp = None
        max = 0
        if edus:
            for edu in edus:
                if edu.edu_level.value > max:
                    max = edu.edu_level.value
                    temp = edu
        return temp

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
    duty = db.Column(db.String(32))
    # 单位
    dept = db.Column(db.String(64))
    # 任职文号
    identifier = db.Column(db.String(64))

    def to_json(self):
        data = {}
        data['id'] = self.id
        data['change_time'] = time2str(self.change_time)
        data['work_time'] = time2str(self.work_time)
        data['duty'] = self.duty
        data['dept'] = self.dept
        data['identifier'] = self.identifier
        return data

    @staticmethod
    def from_json(data):
        _id = data.get('id')
        dept = data.get('dept')
        duty = data.get('duty')
        if dept is None or duty is None:
            return None
        if _id is None:
            temp = Resume(duty=duty, dept=dept)
        else:
            temp = Resume.query.get_or_404(_id)
        temp.change_time = str2time(data.get('change_time'))
        temp.work_time = str2time(data.get('work_time'))
        temp.identifier = data.get('identifier')
        return temp

    def __repr__(self):
        return "<{}的简历>".format(self.duty)


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

    def to_json(self):
        data = {}
        data['id'] = self.id
        data['time'] = time2str(self.time)
        data['dept'] = self.dept
        data['reason'] = self.reason
        data['result'] = self.result
        data['remarks'] = self.remarks
        return data

    @staticmethod
    def from_json(data):
        _id = data.get('id')
        result = data.get('result')
        if result is None:
            return None
        if _id:
            rp = RAndP.query.get_or_404(_id)
        else:
            rp = RAndP(result=result)
        rp.time = str2time(data.get('time'))
        rp.dept = data.get('dept')
        rp.reason = data.get('reason')
        rp.remarks = data.get('remarks')
        return rp

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
    # 毕业院校
    edu_name = db.Column(db.String(128))
    # 专业名
    department = db.Column(db.String(64))
    # 学位
    degree = db.Column(db.String(64))
    # 学习形式
    learn_id = db.Column(db.Integer, db.ForeignKey('learn_forms.id'))
    # 备注
    remarks = db.Column(db.String(300))

    def to_json(self):
        data = {}
        data['id'] = self.id
        data['lv'] = self.edu_level.level
        data['enrolment_time'] = time2str(self.enrolment_time)
        data['graduation_time'] = time2str(self.graduation_time)
        data['edu_name'] = self.edu_name
        data['department'] = self.department
        data['degree'] = self.degree
        data['learn_form'] = self.learn_form.name
        return data

    @staticmethod
    def from_json(data):
        _id = data.get('id')
        edu_name = data.get('edu_name')
        edu_level = EduLevel.query.get(data.get('edu_level_id'))
        if edu_level is None or edu_name is None:
            return None
        if _id:
            edu = Education.query.get_or_404(_id)
        else:
            edu = Education(edu_level=edu_level, edu_name=edu_name)
        edu.department = data.get('department')
        edu.degree = data.get('degree')
        edu.remarks = data.get('remarks')
        edu.enrolment_time = str2time(data.get('enrolment_time'))
        edu.graduation_time = str2time(data.get('graduation_time'))
        edu.learn_form = LearnForm.query.get(data.get('learn_id'))
        return edu

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

    @staticmethod
    def to_arr():
        edu_lvs = EduLevel.query.all()
        return [[lv.id, lv.level] for lv in edu_lvs]

    def __repr__(self):
        return "<学历: {}>".format(self.level)


class LearnForm(db.Model):
    __tablename__ = 'learn_forms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    edu = db.relationship('Education', backref='learn_form', lazy='joined')

    @staticmethod
    def to_arr():
        lfs = LearnForm.query.all()
        return [[lf.id, lf.name] for lf in lfs]

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

    def to_json(self):
        data = {}
        data['id'] = self.id
        data['relationship'] = self.relationship
        data['name'] = self.name
        data['age'] = self.age
        data['p_c'] = self.p_c
        data['workplace'] = self.workplace
        return data

    @staticmethod
    def from_json(data):
        _id = data.get('id')
        name = data.get('name')

        if name is None:
            return None

        if _id:
            family = Family.query.get_or_404(_id)
        else:
            family = Family(name=name)

        family.relationship = data.get('relationship')
        family.age = data.get('age')
        family.p_c = data.get('p_c')
        family.workplace = data.get('workplace')

        return family

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
        if data is None and data.get('name') is None:
            abort(403)
        _id = data.get('id')
        name = data.get('name')
        if name == '':
            return None
        duty_level_id = data.get('duty_level_id')
        if name is None or duty_level_id is None:
            return None
        if _id is not None:
            temp = Duty.query.get_or_404(_id)
        else:
            temp = Duty.query.filter_by(name=name).first()
            if temp is None:
                temp = Duty(name=name)
        temp.duty_level = DutyLevel.query.get_or_404(duty_level_id)
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

    def to_json(self):
        data = {}
        if self.name:
            data['id'] = self.id
            data['name'] = self.name.name
            data['dept'] = self.name.dept.name
            data['lv'] = self.name.lv.name
            data['major'] = self.major
            data['remarks'] = self.remarks
            data['page_no'] = self.page_no
            data['engage'] = '是' if self.engage else '否'
            data['get_time'] = time2str(self.get_time)
            data['engage_time'] = time2str(self.engage_time)
        return data

    @staticmethod
    def from_json(data):
        name = TitleName.query.get(data.get('name_id'))
        major = data.get('major')
        _id = data.get('id')
        if name is None or major is None:
            return None
        if _id is None:
            temp = Title(name=name)
        else:
            temp = Title.query.get_or_404(_id)
        temp.major = major
        temp.remarks = data.get('remarks')
        temp.page_no = data.get('page_no')
        if data.get('engage') == "true":
            temp.engage = True
        temp.engage_time = str2time(data.get('engage_time'))
        temp.get_time = str2time(data.get('get_time'))
        return temp

    def __repr__(self):
        return "{}".format(self.name)


class TitleName(db.Model):
    __tablename__ = 'title_names'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    titles = db.relationship('Title', backref='name', lazy='dynamic')
    title_lv_id = db.Column(db.Integer, db.ForeignKey('title_lv.id'))
    title_dept_id = db.Column(db.Integer, db.ForeignKey('title_dept.id'))

    @staticmethod
    def to_arr():
        res = []
        names = TitleName.query.all()
        for temp in names:
            l = []
            l.append(temp.id)
            l.append(temp.name)
            if temp.dept:
                l.append(temp.dept.name)
            else:
                l.append('无')
            if temp.lv:
                l.append(temp.lv.name)
            else:
                l.append('无')
            res.append(l)
        return res

    def __repr__(self):
        return "<职称名: {}>".format(self.name)


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

    @staticmethod
    def to_arr():
        states = State.query.all()
        return [[state.id, state.name] for state in states]

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