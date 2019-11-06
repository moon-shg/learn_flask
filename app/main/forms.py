from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

#创建一个表单
class NameForm(FlaskForm):
	# Validator 为验证函数组成的列表，其中DataRequired（）函数确保提交内容不为空
	name = StringField("你的名字是？", validators=[DataRequired()])
	submit = SubmitField('确认')
