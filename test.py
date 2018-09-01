import datetime
from app.models import db, Personnel, Dept


def add_personnel():
    """测试添加成员 也作为添加实验数据用"""
    p = Personnel(name='果子')
    p.sex = '男'
    p.birthday = datetime.date(1991, 4, 13)
    p.id_card = '41040222222222222222222222'
    p.cadre_id = '1231111111'
    _dept = Dept.query.get_or_404(5)
    p.dept = _dept
    db.session.add(p)
    db.session.commit()


