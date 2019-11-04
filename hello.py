from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from threading import Thread

# 当前文件夹的绝对路径？
basedir = os.path.abspath(os.path.dirname(__file__))

#设置配置变量
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hard to guess string'

#配置Flask-Mail使用QQ邮箱
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[孙彤]'
app.config['FLASKY_MAIL_SENDER'] = 'ST<393773661@qq.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

#初始化app
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

#添加一个shell上下文，让 flask shell 自动导入数据库实例和模型
@app.shell_context_processor
def make_shell_context():
	return dict(db=db, User=User, Role=Role)

#设置路由表
@app.route('/', methods=['GET','POST'])
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
			if app.config['FLASKY_ADMIN']:
				send_email(app.config['FLASKY_ADMIN'], 'NEW USER', 'mail/new_user', user = user)
		else: 
			session['known'] = True
		session['name'] = form.name.data # 将表单接受到的字符串存储在 用户会话 session 字典中
		form.name.data = ''
		# old_name = session.get('name')
		# if old_name is not None and old_name != form.name.data:
		# 	flash('你好像换了个名字！')
		# session['name'] = form.name.data # 将表单接受到的字符串存储在 用户会话 session 字典中
		return redirect(url_for('index'))
	return render_template('index.html', current_time=datetime.utcnow(), form = form, name = session.get('name'), known=session.get('known',False))

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

#创建异步发送邮件的函数，使处理发送邮件的请求在后台线程中运行
def send_async_email(app, msg): 
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, \
		sender = app.config['FLASKY_MAIL_SENDER'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr

#创建一个表单
class NameForm(FlaskForm):
	# Validator 为验证函数组成的列表，其中DataRequired（）函数确保提交内容不为空
	name = StringField("你的名字是？", validators=[DataRequired()])
	submit = SubmitField('确认')

#创建一个数据库
class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref='role', lazy='dynamic')
	# 定义调用查询语句 self.query() 时返回语句的格式
	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username
