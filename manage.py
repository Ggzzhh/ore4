#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User, Role

app = create_app('development')
manager = Manager(app)
migrate = Migrate(app, db)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, user=User, role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def init():
    from app.models import run_only
    run_only()

if __name__ == "__main__":
    manager.run()





