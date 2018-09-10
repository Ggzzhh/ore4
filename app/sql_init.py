# -*- coding: utf-8 -*-
from app import db

from app.models import LearnForm, EduLevel, State


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