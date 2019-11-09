from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import User, Role 

#创建一个表单
class NameForm(FlaskForm):
	# Validator 为验证函数组成的列表，其中DataRequired（）函数确保提交内容不为空
	name = StringField("你的名字是？", validators=[DataRequired()])
	submit = SubmitField('确认')


# 资料编辑表单
class EditProfileForm(FlaskForm):
	name = StringField('真实姓名', validators=[Length(0,64)])
	location = StringField('居住地址', validators=[Length(0,64)])
	about_me = TextAreaField('个人简介')
	submit = SubmitField('提交')

# 资料编辑表单 - 管理员用
class EditProfileAdminForm(FlaskForm):
	email = StringField('电子邮箱', validators=[DataRequired(),Length(1,64),Email()])
	username = StringField('用户名', validators=[DataRequired(),Length(1,64),
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名由字母，数字，小数点和下划线构成')])
	confirmed = BooleanField('已认证')
	role = SelectField('用户组', coerce=int)
	name = StringField('真实姓名', validators=[Length(0,64)])
	location = StringField('地址', validators=[Length(0,64)])
	about_me = TextAreaField('个人简介')
	submit = SubmitField('提交')


	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args,**kwargs)
		self.role.choices = [(role.id, role.name) \
			for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and \
			User.query.filter_by(email=field.data).first():
			raise VaildationError('该邮箱已被注册')

	def validata_username(self,field):
		if field.data != self.user.username and \
			User.query.filter_by(username=field.data).first():
			raise VaildationError('用户名已存在')


# 博客文章表单
class PostForm(FlaskForm):
	body = TextAreaField("what's on your mind?", validators=[DataRequired()])
	submit = SubmitField('提交')