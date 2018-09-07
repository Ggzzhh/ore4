#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User, Role, Dept, Personnel, DeptPro, Duty, DutyLevel,\
    Title, TitleLv, TitleDept, EduLevel, State, System, Education,\
    Resume

app = create_app('development')
manager = Manager(app)
migrate = Migrate(app, db)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, user=User, role=Role, dept=Dept,
                per=Personnel, duty=Duty, title=Title)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def init():
    from app.models import run_only
    from app.sql_init import init_edu_lv, init_learn_form
    # run_only()
    init_edu_lv()
    init_learn_form()


@manager.command
def ex_test():
    from app.handle_excel import UNIT, _Duty, _Title
    unit = UNIT()
    duty = _Duty()
    title = _Title()
    unit.init_system()
    unit.init_dept_pro()
    unit.init_dept()
    duty.init_duty_lv()
    duty.init_duty()
    title.init_t_dept()
    title.init_t_lvs()
    title.init_t()
    db.session.commit()


@manager.command
def db_test():
    from test import add_personnel
    add_personnel()


if __name__ == "__main__":
    manager.run()





