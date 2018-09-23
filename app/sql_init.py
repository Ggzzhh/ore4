# -*- coding: utf-8 -*-
from random import sample

from app import db

from app.models import LearnForm, EduLevel, State, Nation, Personnel, Duty


def init_learn_form():
    l = ["统招", "脱产", "业余", "函授", "自学"]
    for temp in l:
        res = LearnForm.query.filter_by(name=temp).first()
        if res is None:
            res = LearnForm(name=temp)
            db.session.add(res)
    print("学习形式写入完毕!")


def init_edu_lv():
    l = [["小学", 1], ["初中", 2],
         ["中专/高中", 3], ["专科", 4],
         ["本科", 5], ["硕士研究生", 6],
         ["博士研究生", 7]]
    for temp in l:
        res = EduLevel.query.filter_by(level=temp[0]).first()
        if res is None:
            res = EduLevel(level=temp[0])
        res.value = temp[1]
        db.session.add(res)
    print("学历写入完毕!")


def init_state():
    l = ["在职：管理人员", "在职：专技人员", "在职：一般管理人员",
         "协理", "调离", "退休", "去世"]
    for temp in l:
        res = State.query.filter_by(name=temp).first()
        if res is None:
            state = State(name=temp)
            db.session.add(state)
    print("状态写入完毕!")


def init_nation():
    strs = "汉族、蒙古族、回族、藏族、维吾尔族、苗族、彝族、" \
           "壮族、布依族、朝鲜族、满族、侗族、瑶族、白族、土家族、" \
           "哈尼族、哈萨克族、傣族、黎族、僳僳族、佤族、畲族、高山族、" \
           "拉祜族、水族、东乡族、纳西族、景颇族、柯尔克孜族、土族、达斡尔族、" \
           "仫佬族、羌族、布朗族、撒拉族、毛南族、仡佬族、锡伯族、阿昌族、普米族、" \
           "塔吉克族、怒族、乌孜别克族、俄罗斯族、鄂温克族、德昂族、保安族、裕固族、" \
           "京族、塔塔尔族、独龙族、鄂伦春族、赫哲族、门巴族、珞巴族、基诺族"
    l = strs.split('、')

    for nation in l:
        res = Nation.query.filter_by(name=nation).first()
        if res is None:
            na = Nation(name=nation)
        db.session.add(na)

    print('民族添加完毕')


def add_per():
    duties = Duty.query.all()

    for i in range(20, 2000):
        duty = sample(duties, 1)[0]
        per = Personnel(name="test{}".format(i), id_card=i+30000, duty=duty)
        db.session.add(per)
        print("+1 啊哈哈哈")