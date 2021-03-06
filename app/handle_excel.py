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
        self._fields = list(FIELDS.keys())
        self.edu_fields = ['学历', '入学时间', '毕业时间', '院校', '专业', '学习形式']
        self.family_fields = ['称谓', '姓名', '年龄', '政治面貌', '工作单位及职务']

    def make_sample_file(self, pers):
        sheet1 = self.f.add_sheet(u'sheet1', cell_overwrite_ok=True)
        rows = self._fields
        col = 0
        rows.append('简历')
        rows.append('奖惩情况')

        # 添加九个学历列
        for i in range(1, 10):
            for field in self.edu_fields:
                rows.append(field + str(i))

        # 添加九个家庭成员
        for i in range(1, 10):
            for field in self.family_fields:
                rows.append(field + str(i))

        # 生成第一行
        for i in range(len(rows)):
            sheet1.write(0, i, rows[i], self.make_style(u'微软雅黑', 12, 1))
            sheet1.col(i).width = 0x0d00
            sheet1.col(i).height = 500

        for per in pers:
            col += 1
            i = 0
            data = per.to_json()
            for key in list(FIELDS.keys()):
                sheet1.write(col, i, data.get(FIELDS[key]))
                i += 1

            resumes = data.get('resumes')
            if resumes:
                resume = ""
                for r in resumes:
                    r = r.to_json()
                    temp = [r.get('work_time') or '空',
                            r.get('dept') or '空',
                            r.get('duty') or '空',
                            r.get('identifier') or '空']
                    resume += " ".join(temp)
                    resume += "\n"
                sheet1.write(col, i, resume)
                i += 1
            else:
                i += 1

            r_and_ps = data.get('r_and_ps')
            r_and_p = ""
            for rp in r_and_ps:
                rp = rp.to_json()
                temp = [
                    rp.get('time') or '空',
                    rp.get('dept') or '空',
                    rp.get('reason') or '空',
                    rp.get('result') or '空',
                    rp.get('remarks') or '空',
                    ]
                r_and_p += " ".join(temp)
                r_and_p += "\n"
            sheet1.write(col, i, r_and_p)
            i += 1

            edus = list(data.get('edus'))
            while len(edus) < 9:
                edus.append('')
            for edu in edus:
                if edu and edu.to_json():
                    edu = edu.to_json()
                    sheet1.write(col, i, edu.get('lv') or "")
                    i += 1
                    sheet1.write(col, i, edu.get('enrolment_time') or "")
                    i += 1
                    sheet1.write(col, i, edu.get('graduation_time') or "")
                    i += 1
                    sheet1.write(col, i, edu.get('edu_name') or "")
                    i += 1
                    sheet1.write(col, i, edu.get('department') or "")
                    i += 1
                    sheet1.write(col, i, edu.get('learn_form') or "")
                    i += 1
                else:
                    for j in range(6):
                        sheet1.write(col, i, "")
                        i += 1

            families = list(data.get('families'))
            while len(families) < 9:
                families.append('')
            for family in families:
                if family:
                    family = family.to_json()
                    sheet1.write(col, i, family.get('relationship') or "")
                    i += 1
                    sheet1.write(col, i, family.get('name') or "")
                    i += 1
                    sheet1.write(col, i, family.get('age') or "")
                    i += 1
                    sheet1.write(col, i, family.get('p_c') or "")
                    i += 1
                    sheet1.write(col, i, family.get('workplace') or "")
                    i += 1
                else:
                    for j in range(5):
                        sheet1.write(col, i, "")
                        i += 1

        self.f.save('files/' + self.file_name)
        return self.file_name

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

    def file2json(self, src):
        file = xlrd.open_workbook(src)
        sheet = file.sheet_by_index(0)
        nrow = sheet.nrows
        ncol = sheet.ncols
        fields = self._fields
        result = []

        def check_excel(names, fields):
            for field in fields:
                if field not in names:
                    return True
            return False

        if ncol != 145 or check_excel(sheet.row_values(0), fields):
            raise TypeError('表格错误！请下载示例表格，在其中加入内容并上传！')

        for i in range(ncol):
            if sheet.cell(1, i).ctype == 3:
                raise TypeError('Excel中存在时间格式！请设置单元格格式为文本！')
        rows = self._fields

        for i in range(1, nrow):
            temp = sheet.row_values(i)
            temp_dict = {}
            for key in rows:
                temp_dict[FIELDS[key]] = temp.pop(0)

            temp_dict['resumes'] = []
            temp_dict['r_and_ps'] = []

            resumes = temp.pop(0).split('\n')
            r_and_ps = temp.pop(0).split('\n')

            for resume in resumes:
                t = {}
                resume = resume.split(' ')
                if len(resume) < 2 or resume[0] == '':
                    break
                while len(resume) < 4:
                    resume.append('空')
                t['work_time'] = resume[0]
                t['dept'] = resume[1]
                t['duty'] = resume[2]
                t['identifier'] = resume[3]
                temp_dict['resumes'].append(t)

            for rp in r_and_ps:
                t = {}
                rp = rp.split(' ')
                if len(resume) < 2 or resume[0] == '':
                    break
                while len(rp) < 5:
                    rp.append('空')
                t['time'] = rp[0]
                t['dept'] = rp[1]
                t['reason'] = rp[2]
                t['result'] = rp[3]
                t['remarks'] = rp[4]
                temp_dict['r_and_ps'].append(t)

            edus = []
            for i in range(9):
                edu = {}
                edu['edu_level'] = temp.pop(0)
                edu['enrolment_time'] = temp.pop(0)
                edu['graduation_time'] = temp.pop(0)
                edu['edu_name'] = temp.pop(0)
                edu['department'] = temp.pop(0)
                edu['learn'] = temp.pop(0)
                for key in edu.keys():
                    if edu[key] != '' and edu[key] and len(edu[key]) > 1:
                        edus.append(edu)
                        break
            temp_dict['edus'] = edus

            families = []
            for i in range(9):
                family = {}
                family['relationship'] = temp.pop(0)
                family['name'] = temp.pop(0)
                family['age'] = temp.pop(0)
                family['p_c'] = temp.pop(0)
                family['workplace'] = temp.pop(0)
                for key in family.keys():
                    if family[key] != '' and len(family[key]) > 1:
                        families.append(family)
                        break
            temp_dict['families'] = families

            result.append(temp_dict)
        return result


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

