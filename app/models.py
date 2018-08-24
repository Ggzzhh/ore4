# -*- coding: utf-8 -*-
import html
import hashlib
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    if user_id:
        user = User.query.get(int(user_id))
        return user
    return None


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<角色: %r>' % self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    retry_count = db.Column(db.Integer, default=10)
    disable_time = db.Column(db.DateTime)
    dept_id = db.Column(db.Integer, db.ForeignKey('depts.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.role:
            self.role = Role.query.filter_by(name='user').first()

    @property
    def password(self):
        raise AttributeError("这不是一个可读属性")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role.name == 'admin'

    def __repr__(self):
        return '<用户名: %r>-%r' % (self.username, self.role)


class Dept(db.Model):
    __tablename__ = 'depts'
    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='dept')


def run_only():

    def register_role():
        db.drop_all()
        db.create_all()
        admin = Role(name='admin')
        leader = Role(name='leader')
        cadre = Role(name='cadre')
        staff = Role(name='staff')
        db.session.add(admin)
        db.session.add(leader)
        db.session.add(cadre)
        db.session.add(staff)
        db.session.commit()

    def register_admin():
        only_admin = User(username=current_app.config['ADMIN_USERNAME'])
        only_admin.password = current_app.config['ADMIN_PASSWORD']
        only_admin.role = Role.query.filter_by(name='admin').first()
        print(only_admin)
        db.session.add(only_admin)
        db.session.commit()

    register_role()
    register_admin()
    print('ok')