from datetime import datetime
from flash import render_template, session, redirect, url_for, current_app
from . import main
from .forms import NameForm
from .. import db
from ..models import User

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

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)
