from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy

# 当前文件夹的绝对路径？
basedir = os.path.abspath(os.path.dirname(__file__))

#设置配置变量
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.jion(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hard to guess string'

#初始化app
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

@app.route('/', methods=['GET','POST'])
def index():
	form = NameForm()
	# 验证提交的表单元素
	if form.validate_on_submit():
		old_name = session.get('name')
		if old_name is not None and old_name != form.name.data:
			flash('你好像换了个名字！')
		session['name'] = form.name.data # 将表单接受到的字符串存储在 用户会话 session 字典中
		return redirect(url_for('index'))
	return render_template('index.html', current_time=datetime.utcnow(), form = form, name = session.get('name'))

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

class NameForm(FlaskForm):
	# Validator 为验证函数组成的列表，其中DataRequired（）函数确保提交内容不为空
	name = StringField("你的名字是？", validators=[DataRequired()])
	submit = SubmitField('确认')

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref='role')

	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username
