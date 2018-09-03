# -*- coding: utf-8 -*-
from pyexcel_xlsx import get_data

from app import db
from app.models import System, Dept, DeptPro, DutyLevel, Duty, Title, \
    TitleDept, TitleLv


class UNIT:
    def __init__(self):
        self.excel_unit = 'excel/单位分类.xlsx'

    def init_system(self):
        data = get_data(self.excel_unit)['系统']
        for system in data:
            res = System.query.filter_by(system_name=system[0]).first()
            if res is None:
                s = System(system_name=system[0])
                db.session.add(s)
        print('系统分类更新完毕')

    def init_dept_pro(self):
        data = get_data(self.excel_unit)['单位属性']
        for pro in data:
            res = DeptPro.query.filter_by(dept_pro_name=pro[0]).first()
            if res is None:
                s = DeptPro(dept_pro_name=pro[0])
                db.session.add(s)
        print('单位属性分类更新完毕')

    def init_dept(self):
        data = get_data(self.excel_unit)['单位']
        for dept in data:
            res = Dept.query.filter_by(dept_name=dept[0]).first()
            if res is None:
                system = System.query.filter_by(system_name=dept[1]).first()
                dept_pro = DeptPro.query \
                    .filter_by(dept_pro_name=dept[2]).first()
                _dept = Dept(dept_name=dept[0])
                if system:
                    _dept.system = system
                if dept_pro:
                    _dept.dept_pro = dept_pro
                db.session.add(_dept)
                message = '插入完成'
            else:
                message = '开始更新所属职务属性以及其系统'
                res.dept_pro = DeptPro.query \
                    .filter_by(dept_pro_name=dept[2]).first()
                res.system = System.query \
                    .filter_by(system_name=dept[1]).first()
                db.session.add(res)
            print(dept[0] + message)
    print('单位分类更新完毕')


class _Duty:
    def __init__(self):
        excel_unit = 'excel/职务.xlsx'
        data = get_data(excel_unit)
        self.duties= data['Sheet1']
        self.lvs = data['Sheet2']

    def init_duty_lv(self):
        for lv in self.lvs:
            res = DutyLevel.query.filter_by(name=lv[0]).first()
            if res is None:
                temp = DutyLevel(name=lv[0])
                temp.value = lv[1]
                db.session.add(temp)
            else:
                res.value = lv[1]
                db.session.add(res)
        print('职称级别数据已更新')

    def init_duty(self):

        for _duty in self.duties:
            res = Duty.query.filter_by(name=_duty[0]).first()
            lv = ''
            if len(_duty) >= 2:
                lv = DutyLevel.query.filter_by(name=_duty[1]).first()
            if res is None:
                temp = Duty(name=_duty[0])
                if lv:
                    temp.duty_level = lv
                db.session.add(temp)
            else:
                if lv:
                    res.duty_level = lv
                db.session.add(res)
        print('职称级别数据已更新\n')


class _Title:
    def __init__(self):
        excel_unit = 'excel/职称.xlsx'
        data = get_data(excel_unit)
        self.t = data['Sheet1']
        self.lvs = data['Sheet2']
        self.depts = data['Sheet3']

    def init_t(self):
        for t in self.t:
            res = Title.query.filter_by(name=t[0]).first()
            lv = ''
            dept = ''
            if len(t) >= 2:
                lv = TitleLv.query.filter_by(name=t[1]).first()
            if len(t) >= 3:
                dept = TitleDept.query.filter_by(name=t[2]).first()
            if res is None:
                temp = Title(name=t[0])
                if lv:
                    temp.title_lv = lv
                if dept:
                    temp.title_dept = dept
                db.session.add(temp)
            else:
                if lv:
                    res.title_lv = lv
                if dept:
                    res.title_dept = dept
                db.session.add(res)
        print('职称信息更新完毕')

    def update_title(self):
        for t in self.t:
            res = Title.query.filter_by(name=t[0]).first()
            lv = ''
            dept = ''
            if len(t) >= 2:
                lv = TitleLv.query.filter_by(name=t[1]).first()
            if len(t) >= 3:
                dept = TitleDept.query.filter_by(name=t[2]).first()
            if res:

                if lv and lv.name != res.title_lv.name:
                    res.title_lv = lv
                elif lv is None and len(t) >= 2:
                    lv = self.new_title_lv(t[1])
                    if lv:
                        res.lv = lv
                else:
                    pass

                if dept and dept.name != res.title_dept.name:
                    res.title_dept = dept
                elif dept is None and len(t) >= 3:
                    dept = self.new_title_dept(t[2])
                    if dept:
                        res.dept = dept
                else:
                    pass

    @staticmethod
    def new_title_lv(name):
        if name is None:
            return None
        try:
            temp = Title(name=name)
            db.session.add(temp)
            db.session.commit()
            return temp
        except:
            return None

    @staticmethod
    def new_title_dept(name):
        if name is None:
            return None
        try:
            temp = Dept(name=name)
            db.session.add(temp)
            db.session.commit()
            return temp
        except:
            return None