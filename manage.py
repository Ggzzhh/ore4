#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand, upgrade

from app import create_app, db
from app.models import User, Role, Dept, Personnel, DeptPro, Duty, DutyLevel,\
    Title, TitleLv, TitleDept, EduLevel, State, System, Education,\
    Resume, RAndP

# app = create_app('development')
app = create_app('production')
manager = Manager(app)
migrate = Migrate(app, db)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, user=User, role=Role,
                per=Personnel, duty=Duty, title=Title,
                edu=Education, rp=RAndP, dept=Dept)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def init_admin():
    from app.models import init_admin
    init_admin()


@manager.command
def init():
    from app.handle_excel import UNIT, _Duty, _Title
    from app.sql_init import init_edu_lv, init_learn_form, \
        init_state, init_nation
    upgrade()
    unit = UNIT()
    duty = _Duty()
    title = _Title()
    init_edu_lv()
    init_learn_form()
    init_state()
    init_nation()
    unit.init_system()
    unit.init_dept_pro()
    unit.init_dept()
    duty.init_duty_lv()
    duty.init_duty()
    title.init_t_dept()
    title.init_t_lvs()
    title.init_t()
    db.session.commit()


if __name__ == "__main__":
    manager.run()





