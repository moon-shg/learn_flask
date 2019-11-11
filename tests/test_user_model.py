import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, Role, AnonymousUser, Permission, Follow


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


	# 验证时间戳
	def test_timestamps(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		self.assertTrue((datetime.utcnow()-u.member_since).total_seconds() < 3)
		self.assertTrue((datetime.utcnow()-u.last_seen).total_seconds() < 3)

	# 检验before_request（请求钩子）中的ping函数
	def test_ping(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		time.sleep(2)
		last_seen_before = u.last_seen
		u.ping()
		self.assertTrue(u.last_seen>last_seen_before)

	# 检验关注关系表
	def test_follows(self):
		u1 = User(email='123@123.com', password='cat')
		u2 = User(email='456@456.com', password='dog')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		self.assertFalse(u1.is_following(u2))
		self.assertFalse(u1.is_followed_by(u2))
		timestamp_before = datetime.utcnow()
		u1.follow(u2)
		db.session.add(u1)
		db.session.commit()
		timestamp_after = datetime.utcnow()
		self.assertTrue(u1.is_following(u2))
		self.assertFalse(u1.is_followed_by(u2))	
		self.assertTrue(u2.is_followed_by(u1))
		self.assertFalse(u2.is_following(u1))
		self.assertTrue(u1.followed.count()==2)
		self.assertTrue(u2.followers.count()==2)
		f = u1.followed.all()[-1]
		self.assertTrue(f.followed == u2)
		self.assertTrue(timestamp_before<=f.timestamp<=timestamp_after)		
		self.assertTrue(timestamp_after>timestamp_before)
		f = u2.followers.all()[-1]
		self.assertTrue(f.followers == u1)
		u1.unfollow(u2)
		db.session.add(u1)
		db.session.commit()
		self.assertTrue(u1.followed.count()==1)
		self.assertTrue(u2.followers.count()==1)
		self.assertTrue(Follow.query.count()==2)
		u2.follow(u1)
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		db.session.delete(u2)
		db.session.commit()
		self.assertTrue(Follow.query.count()==1)

