# -*- coding: utf-8 -*-
import os

import xlrd, xlwt
from pyexcel_xlsx import get_data
from flask import session

from app import db
from app.models import System, Dept, DeptPro, DutyLevel, Duty, TitleName, \
    TitleDept, TitleLv
from app.const import FIELDS


class MakeExcel:
    def __init__(self, fields=None, file_name=None):
        self.directory = os.getcwd()
        self.file_name = u"结果.xls" if file_name is None else file_name
        self.fields = [] if \
            fields is None or not isinstance(fields, list) else fields
        self.f = xlwt.Workbook()

    def make_sample_file(self):
        sheet1 = self.f.add_sheet(u'sheet1', cell_overwrite_ok=True)
        rows = list(FIELDS.keys())
        edu_fields = ['学历', '入学时间', '毕业时间', '院校', '专业', '学习形式']
        family_fields = ['称谓', '姓名', '年龄', '政治面貌', '工作单位及职务']

        # 添加九个学历列
        for i in range(1, 10):
            for field in edu_fields:
                rows.append(field + str(i))

        # 添加九个家庭成员
        for i in range(1, 10):
            for field in family_fields:
                rows.append(field + str(i))

        # 生成第一行
        for i in range(len(rows)):
            sheet1.write(0, i, rows[i], self.make_style(u'微软雅黑', 12, 1))
            sheet1.col(i).width = 0x0d00
            sheet1.col(i).height = 500

        self.f.save(self.file_name)

    def make_result_file(self, pers):
        sheet = self.f.add_sheet(u'sheet1', cell_overwrite_ok=True)
        rows = self.fields

        for i in range(0, len(rows)):
            sheet.write(0, i, rows[i], self.make_style(u'微软雅黑', 12, 1))
            sheet.col(i).width = 0x0d00
            sheet.col(i).height = 500
            for j in range(1, len(pers)+1):
                sheet.write(j, i, pers[j-1]['data'][i])

        self.f.save('files/' + self.file_name)
        return self.file_name

    def make_roster_file(self, ids):
        sheet = self.f.add_sheet(u'sheet1', cell_overwrite_ok=True)
        y = 0
        x = 2
        rows0 = ["单位", "姓名", "性别", "民族", "出生", "年龄", "工作时间", "入党时间", "职务", "级别"]
        edus = ["学历", "毕业时间", "院校", "专业"]
        rows0plus = ["籍贯", "职称", "身份", "任副科级时间", "任正科级时间", "任现职时间", "备注"]
        fields = ["name", "sex", "nation", "birthday", "age", "work_time",
                  "party_member", "duty_name", "duty_lv", "max_edu_lv",
                  "max_edu_time", "max_edu_name", "max_edu_dept",
                  "at_edu_lv", "at_edu_time", "at_edu_name", "at_edu_dept",
                  "ot_edu_lv", "ot_edu_time", "ot_edu_name", "ot_edu_dept",
                  "native_place", "title_name", "identity", "deputy_sc_time",
                  "sc_time", "position_time", "remarks"]

        # 开始写入标题
        for row in rows0:
            sheet.write_merge(0, 1, y, y, row, self.make_style(u'微软雅黑', 12, 1))
            y += 1
        # 写入学历
        sheet.write_merge(0, 0, y, y + 3, "最高学历",
                          self.make_style(u'微软雅黑', 12, 1))
        for edu in edus:
            sheet.write(1, y, edu, self.make_style(u'微软雅黑', 12, 1))
            y += 1

        sheet.write_merge(0, 0, y, y+3, "全日制学历",
                          self.make_style(u'微软雅黑', 12, 1))
        for edu in edus:
            sheet.write(1, y, edu, self.make_style(u'微软雅黑', 12, 1))
            y += 1

        sheet.write_merge(0, 0, y, y + 3, "在职学历",
                          self.make_style(u'微软雅黑', 12, 1))
        for edu in edus:
            sheet.write(1, y, edu, self.make_style(u'微软雅黑', 12, 1))
            y += 1

        # 开始写入标题+
        for row in rows0plus:
            sheet.write_merge(0, 1, y, y, row,
                              self.make_style(u'微软雅黑', 12, 1))
            y += 1

        for id in ids:
            dept = Dept.query.get(id)
            if dept:
                count = dept.personnels.count()
                for i in range(29):
                    if i == 0:
                        sheet.write(x, i, dept.dept_name, self.make_style(
                            u'微软雅黑'))
                    elif i == 3:
                        sheet.write(x, i, count, self.make_style(u'微软雅黑'))
                    else:
                        sheet.write(x, i, "", self.make_style(u'微软雅黑'))
                    sheet.col(i).width = 0x0d00
                    sheet.col(i).height = 500
                x += 1
                for per in dept.personnels:
                    per = per.to_json()
                    sheet.write(x, 0, "", self.make_style(u'微软雅黑'))
                    for i in range(len(fields)):
                        sheet.write(x, i+1, per.get(fields[i]), self.make_style(u'微软雅黑'))
                    x += 1
            else:
                pass

        self.f.save('files/' + self.file_name)
        return self.file_name

    def make_count_excel(self):
        sheet = self.f.add_sheet(u'sheet1', cell_overwrite_ok=True)
        rows = list(session['count'].keys())
        i = 0

        # 表头
        for row in rows:
            j = 2
            sheet.write_merge(0, 0, i, i+1, row,
                              self.make_style(u'微软雅黑', 12, 1))
            sheet.write(1, i, "名称", self.make_style(u'微软雅黑', 12, 1))
            sheet.write(1, i+1, "人数", self.make_style(u'微软雅黑', 12, 1))
            for field in session['count'][row]['fields']:
                sheet.write(j, i, field['name'], self.make_style(u'微软雅黑'))
                sheet.write(j, i+1, field['count'], self.make_style(u'微软雅黑'))
                j += 1
            sheet.write(j, i, "合计", self.make_style(u'微软雅黑', 14, 1))
            sheet.write(j, i+1, session['count'][row]['count'],
                        self.make_style(u'微软雅黑', 14, 1))
            i += 2

        self.f.save('files/' + self.file_name)
        return self.file_name

    @staticmethod
    def make_style(font_name, color=1, font_color=0, border=1):
        style = xlwt.XFStyle()

        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        if isinstance(color, int):
            pattern.pattern_fore_colour = color
        style.pattern = pattern

        font = xlwt.Font()
        font.name = u'{}'.format(font_name)
        font.colour_index = font_color
        font.bold = True
        style.font = font

        al = xlwt.Alignment()
        al.horz = 0x02  # 设置水平居中
        al.vert = 0x01  # 设置垂直居中
        style.alignment = al

        if border and isinstance(border, int):
            borders = xlwt.Borders()
            borders.right = border
            borders.left = border
            borders.top = border
            borders.bottom = border
            style.borders = borders

        return style


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
                if res.order is None:
                    res.order = 10
                db.session.add(res)
                # print(dept[0] + message)
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
        print('职务级别数据已更新')

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
                if res.order is None or res.order == 0:
                    res.order = 1
                if lv:
                    res.duty_level = lv
                db.session.add(res)
        print('职务数据已更新')


class _Title:
    def __init__(self):
        excel_unit = 'excel/职称.xlsx'
        data = get_data(excel_unit)
        self.t = data['Sheet1']
        self.lvs = data['Sheet2']
        self.depts = data['Sheet3']

    def init_t_dept(self):
        for _dept in self.depts:
            res = TitleDept.query.filter_by(name=_dept[0]).first()
            if res is None:
                temp = TitleDept(name=_dept[0])
                db.session.add(temp)
        print('职称系别数据已更新')

    def init_t_lvs(self):
        for lv in self.lvs:
            res = TitleLv.query.filter_by(name=lv[0]).first()
            if res is None:
                temp = TitleLv(name=lv[0])
                db.session.add(temp)
        print('职称级别数据已更新')

    def init_t(self):
        for t in self.t:
            res = TitleName.query.filter_by(name=t[0]).first()
            lv = ''
            dept = ''
            if len(t) >= 2:
                lv = TitleLv.query.filter_by(name=t[1]).first()
            if len(t) >= 3:
                dept = TitleDept.query.filter_by(name=t[2]).first()
            if res is None:
                temp = TitleName(name=t[0])
                if lv:
                    temp.lv = lv
                if dept:
                    temp.dept = dept
                db.session.add(temp)
            else:
                if lv:
                    res.lv = lv
                if dept:
                    res.dept = dept
                db.session.add(res)
        print('职称信息更新完毕')


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
