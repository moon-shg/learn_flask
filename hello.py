from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.route('/', methods=['GET','POST'])
def index():
	form = NameForm()
	# 验证提交的表单元素
	if form.validate_on_submit():
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
