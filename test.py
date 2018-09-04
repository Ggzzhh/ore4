import datetime
from app.models import db, Personnel, Dept, Title, Per2Title


def add_personnel():
    """测试添加成员 也作为添加实验数据用"""
    l = []
    title1 = Title.query.get_or_404(2)
    title2 = Title.query.get_or_404(4)

    p = Personnel(name='果子')
    p.sex = '男'
    p.birthday = datetime.date(1991, 4, 13)
    p.id_card = '41040222222222222222222222'
    p.cadre_id = '1231111111'
    _dept = Dept.query.get_or_404(4)
    p.dept = _dept
    l.append(p)

    p2 = Personnel(name='呵呵')
    p2.sex = '女'
    p2.birthday = datetime.date(1990, 9, 13)
    p2.id_card = '41040222222222222222222222'
    p2.cadre_id = '1231111111'
    _dept2 = Dept.query.get_or_404(2)
    p2.dept = _dept2
    l.append(p2)

    p2t1 = Per2Title(personnel=p, title=title1, date=datetime.date(1990, 9, 13))
    p2t2 = Per2Title(personnel=p, title=title2, date=datetime.date(1991, 1, 23))
    p2t3 = Per2Title(personnel=p2, title=title1, date=datetime.date(1995, 3,
                                                                    3))
    p2t4 = Per2Title(personnel=p2, title=title2, date=datetime.date(1999, 11,
                                                                    15))
    l.append(p2t1)
    l.append(p2t2)
    l.append(p2t3)
    l.append(p2t4)

    db.session.add_all(l)


