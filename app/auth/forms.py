from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1,64), Email])
	password = PasswordField('password', validators=[DataRequired()])
	remember_me = BooleanField('保持登录状态')
	submit = SubmitField('登录')