from . import db
from werkzeug.security import generate_password_hash, check_password_hash


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
	# 生成密码散列
	password_hash = db.Column(db.String(128))
	
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
	
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	# 设置print()函数的输出格式
	def __repr__(self):
		return '<User %r>' % self.username


