import unittest
import re
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_home_page(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertTrue('你好' in response.get_data(as_text=True))

	# 注册新用户
	def test_register_and_login(self):
		response = self.client.post('/auth/register', data = {
			'email' : '123@123.com',
			'password' : 'cat',
			'username' : 't123',
			'password2' : 'cat'
			})
		self.assertEqual(response.status_code, 302)

		# 使用新用户登录
		response =  self.client.post('/auth/login', data={
			'email' : '123@123.com',
			'password' : 'cat' 
			}, follow_redirects=True)
		self.assertEqual(response.status_code, 200)
		self.assertTrue('t123' in response.get_data(as_text=True))
		self.assertTrue('您还没有验证' in response.get_data(as_text=True))

		# 发送确认令牌
		user = User.query.filter_by(email='123@123.com').first()
		token = user.generate_confirmation_token()
		response = self.client.get(f'/auth/confirm/{token}', follow_redirects=True)
		# user.confirm(token)
		self.assertEqual(response.status_code, 200)
		self.assertTrue('已认证！' in response.get_data(as_text=True))

		# 退出
		response = self.client.get('/auth/logout', follow_redirects=True)
		self.assertEqual(response.status_code, 200)
		self.assertTrue('已退出登录' in response.get_data(as_text=True))


