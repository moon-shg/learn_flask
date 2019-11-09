from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, flash
from . import main
from .forms import NameForm, EditProfileForm
from .. import db
from ..models import User
from flask_login import login_required, current_user

#设置路由表
@main.route('/', methods=['GET','POST'])
def index():
	form = NameForm()
	# 验证提交的表单元素
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			db.session.commit()
			session['known'] = False
			if current_app.config['FLASKY_ADMIN']:
				send_email(current_app.config['FLASKY_ADMIN'], 'NEW USER', 'mail/new_user', user = user)
		else: 
			session['known'] = True
		session['name'] = form.name.data # 将表单接受到的字符串存储在 用户会话 session 字典中
		form.name.data = ''
		# old_name = session.get('name')
		# if old_name is not None and old_name != form.name.data:
		# 	flash('你好像换了个名字！')
		# session['name'] = form.name.data # 将表单接受到的字符串存储在 用户会话 session 字典中
		return redirect(url_for('.index'))
	return render_template('index.html', current_time=datetime.utcnow(), form = form, name = session.get('name'), known=session.get('known',False))

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user._get_current_object())
		db.session.commit()
		flash("个人资料已更新！")
		return redirect(url_for('.user', username=current_user.username))
	# 设置表单的初始值
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('/edit_profile.html', form=form)
