# -*- coding: utf-8 -*-
from pyexcel_xlsx import get_data

from app import db
from app.models import System, Dept, DeptPro, User


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
            else:
                print(system[0] + '已存在')
        print('系统分类更新完毕')

    def init_dept_pro(self):
        data = get_data(self.excel_unit)['单位属性']
        for pro in data:
            res = DeptPro.query.filter_by(dept_pro_name=pro[0]).first()
            if res is None:
                s = DeptPro(dept_pro_name=pro[0])
                db.session.add(s)
            else:
                print(pro[0] + '已存在')
        print('单位属性分类更新完毕')

    def init_dept(self):
        data = get_data(self.excel_unit)['单位']
        for dept in data:
            res = Dept.query.filter_by(dept_name=dept[0]).first()
            if res is None:
                system = System.query.filter_by(system_name=dept[1]).first()
                dept_pro = DeptPro.query \
                    .filter_by(dept_pro_name=dept[2]).first()
                dept = Dept(dept_name=dept[0])
                if system:
                    dept.system = system
                if dept_pro:
                    dept.dept_pro = dept_pro
                db.session.add(dept)
            else:
                message = '已存在'
                if res.dept_pro is None:
                    res.dept_pro = DeptPro.query \
                        .filter_by(dept_pro_name=dept[2]).first()
                    message += ' 单位属性已插入！'
                if res.system is None:
                    res.system = System.query\
                        .filter_by(system_name=dept[1]).first()
                    message += ' 系统已插入！'
                print(dept[0] + message)
        print('单位分类更新完毕')
