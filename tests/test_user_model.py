import unittest
import time
from app import create_app, db
from app.models import User, Role, AnonymousUser, Permission


class UserModelTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_password_setter(self):
		u = User(password = 'cat')
		self.assertTrue(u.password_hash is not None)

	def test_no_password_getter(self):
		u = User(password = 'cat')
		with self.assertRaises(AttributeError):
			u.password

	def test_password_verification(self):
		u = User(password = 'cat')
		self.assertTrue(u.verify_password('cat'))
		self.assertFalse(u.verify_password('dog'))

	def test_password_salts_are_random(self):
		u = User(password = 'cat')
		u2 = User(password = 'cat')
		self.assertTrue(u.password_hash != u2.password_hash)

	# 验证一个用户生成的token的有效性
	def test_valid_comfirmation_token(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token()
		self.assertTrue(u.confirm(token))

	# 验证不同用户生成的token不能通用
	def test_invalid_comfirmation_token(self):
		u1 = User(password='cat')
		u2 = User(password='dog')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		token = u1.generate_confirmation_token()
		self.assertFalse(u2.confirm(token))

	# 验证token的时效性
	def test_expired_confirmation_token(self):
		u = User(password = 'cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token(1) #设置token的有效时间为1s
		time.sleep(2)
		self.assertFalse(u.confirm(token))


	# 验证角色和权限
	def test_user_role(self):
		u = User(email='asdf@123.com', password='cat')
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE))
		self.assertFalse(u.can(Permission.MODERATE))
		self.assertFalse(u.can(Permission.ADMIN))
	
	# 验证协管员用户权限
	def test_moderator_user(self):
		r = Role.query.filter_by(name='Moderator').first()
		u = User(email='asdf@123.com', password='cat', role=r)
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE))
		self.assertTrue(u.can(Permission.MODERATE))
		self.assertFalse(u.can(Permission.ADMIN))

	# 验证管理员用户权限
	def test_administrator_user(self):
		r = Role.query.filter_by(name='Administrator').first()
		u = User(email='asdf@123.com', password='cat', role=r)
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE))
		self.assertTrue(u.can(Permission.MODERATE))
		self.assertTrue(u.can(Permission.ADMIN))

	# 验证匿名用户权限
	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.FOLLOW))
		self.assertFalse(u.can(Permission.COMMENT))
		self.assertFalse(u.can(Permission.WRITE))
		self.assertFalse(u.can(Permission.MODERATE))
		self.assertFalse(u.can(Permission.ADMIN))