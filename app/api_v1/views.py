# -*- coding: utf-8 -*-
import json

from flask import flash, redirect, url_for, jsonify, \
    current_app, request
from flask_login import logout_user, current_user, login_required

from . import api_v1
from ..models import db, User


@api_v1.route('/update-pwd', methods=["POST"])
@login_required
def update_pwd():
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    res = request.get_json()
    if res is None:
        return jsonify({'error': True, 'error_message': '没有值传递'})
    user = User.query.get_or_404(res['id'])
    if user and res['old_pwd']:
        if user.verify_password(res['old_pwd']):
            user.password = res['pwd']
            db.session.add(user)
            return jsonify({'error': False, 'message': '密码更改成功！'})
    return jsonify({'error': True, 'error_message': '密码错误！'})


@api_v1.route('/logout/<string:username>')
@login_required
def logout(username):
    if username == current_user.username:
        logout_user()
        flash('账号已注销！')
    return redirect(url_for('index.login'))


@api_v1.route('/del-user/<int:id>')
@login_required
def del_user(id):
    if current_user.username != current_app.config['ADMIN_USERNAME']:
        return jsonify({'error': True, 'error_message': '权限不足'})
    user = User.query.get_or_404(id)
    db.session.delete(user)
    return jsonify({'error': False, 'message': '已删除!'})
