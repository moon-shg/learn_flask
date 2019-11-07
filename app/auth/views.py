from flask import render_template, request, url_for, redirect, flash
from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User
from flask_login import login_user, logout_user, login_required
from app import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			next = request.args.get('next')
			if next is None or not next.startswith('/'):
				next = url_for('main.index')
			return redirect(next)
		flash('用户名或密码不正确！')
	return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('已退出登录！')
	return redirect(url_for('main.index'))
	

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, username=form.username.data, password=form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('已成功注册，你现在可以登录了！')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)
