from flask import render_template, request, url_for, redirect, flash
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordForm, ResetPasswordRequestForm
from ..models import User
from flask_login import login_user, logout_user, login_required
from app import db
from ..email import send_email
from flask_login import current_user

# 登录页面
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

# 登出
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('已退出登录！')
	return redirect(url_for('main.index'))
	

# 注册页面
@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, username=form.username.data, password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, "认证您的账户", 'auth/email/confirm', user=user, token=token)
		flash('账户认证邮件已发送至您的邮箱，请前往邮箱认证！')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form=form)


# 账户邮箱确认页面
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		db.session.commit()
		flash('您的账户已认证！')
	else:
		flash('您的验证链接已过期！')
	return redirect(url_for('main.index'))


# 使用before_app_request处理程序过滤未确认账户
@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		# 如果用户已登录，则记录登录时间，并保存到User.last_seen属性中
		current_user.ping()
		if not current_user.confirmed and request.endpoint \
			and request.blueprint != 'auth' and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html', user=current_user)

# 重新发送账户确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, "认证您的账户", 'auth/email/confirm', user=current_user, token=token)
	flash('一封新的认证邮件已经发送至您的邮箱！')
	return redirect(url_for('main.index'))


# 修改密码
@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if not current_user.verify_password(form.old_password.data):
			flash('您输入的密码不正确！')
			return redirect(url_for('auth.change_password'))
		current_user.password = form.new_password.data
		db.session.add(current_user)
		db.session.commit()
		flash('修改密码成功！')
		return redirect(url_for('auth.login'))
	return render_template('auth/change_password.html', form=form)

# 重设密码
@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		if User.query.filter_by(email=form.email.data).first() is not None:
			user = User.query.filter_by(email=form.email.data).first()
			token = user.generate_reset_token()
			send_email(form.email.data, "重置密码", 'auth/email/reset_password',
		 		user=user, token=token)
			flash('重置密码的邮件已发送至您的邮箱，请点击邮件中的链接重置密码！')
			return redirect(url_for('auth.login'))
		flash('您输入的邮箱错误,请重新输入')
		return redirect(url_for('reset_password_request'))
	return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		if User.reset_password(token, form.password.data):
			db.session.commit()
			flash('您的密码已经重置')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=form)


