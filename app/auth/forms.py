from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
	password = PasswordField('password', validators=[DataRequired()])
	remember_me = BooleanField('保持登录状态')
	submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
	email = StringField('邮箱', validators=[DataRequired(), Length(1,64), Email()])
	username = StringField('用户名', validators=[DataRequired(), Length(1,64), 
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
		'用户名必须由大小写英文字母，数字，小数点或下划线构成')])
	password = PasswordField('密码', validators=[
		DataRequired(), EqualTo('password2', message='两次密码不相同')])
	password2 = PasswordField('确认密码', validators=[DataRequired()])
	submit = SubmitField('注册')

def validate_email(self, field):
	if User.query.filter_by(email=field.data).first():
		raise ValidationError('该邮箱已注册！')

def validate_username(self, field):
	if User.query.filter_by(Username=field.data).first():
		raise ValidationError('用户名已被使用！')
