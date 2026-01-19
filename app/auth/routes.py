import os
from functools import wraps

from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, session, Blueprint
from dotenv import load_dotenv
from CRM_LEAS.app.auth import bd
from datetime import datetime


load_dotenv()


auth_bp = Blueprint('auth', __name__, template_folder='templates')




@auth_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        password = request.form.get('password')


        if not all([username, full_name, password]):
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('auth.register'))

        if bd.user_exists(username):
            flash('Пользователь с таким именем уже существует', 'error')
            return redirect(url_for('auth.register'))

        try:
            bd.create_users(username=username, full_name=full_name, password=password)
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Ошибка при регистрации: {str(e)}', 'error')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')



@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([username, password]):
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('auth.login'))

        user = bd.login_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            if not user.role:
                return redirect(url_for('auth.no_role'))
            session['role'] = user.role.name
            flash('Вы успешно вошли в систему!', 'success')
            if user.role.name == 'admin':
                return redirect(url_for('admin.index'))
            elif user.role.name == 'manager':
                return redirect(url_for('manager.index'))
            elif user.role.name == 'expert':
                return redirect(url_for('expert.index'))

        else:
            flash('Неверное имя пользователя или пароль', 'error')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@auth_bp.route('/logout/')
def logout():
    session.clear()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/no-role/')
def no_role():
    return render_template('auth/no_role.html')
