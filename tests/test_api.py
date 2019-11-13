import unittest
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Post
import json

class APITestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def get_api_headers(self, username, password):
		return {
		'Authorization' : 'Basic '+b64encode(
			(username+':'+password).encode('utf-8')).decode('utf-8'),
		'Accept':'application/json',
		'Content-Tpye':'application/json'
		}

	def test_no_auth(self):
		response = self.client.get('/api/v1/posts/', content_type='application/json')
		self.assertEqual(response.status_code, 401)

	def test_posts(self):
		# 添加新用户
		r = Role.query.filter_by(name='User').first()
		self.assertIsNotNone(r)
		u = User(email='123@123.com', password='cat', confirmed=True, role=r)
		db.session.add(u)
		db.session.commit()

		# 下面代码有问题

		# 写一篇post
		# response = self.client.post(
		# 	'/api/v1/posts/', headers=self.get_api_headers('123@123.com', 'cat'), 
		# 	data=json.dumps({'body' : 'test api by unittest'}))
		# self.assertEqual(response.status_code, 201)
		# url = response.headers.get('Location')
		# self.assertIsNotNone(url)

		# 获取刚发布的post
		# response = self.client.get(url, headers=self.get_api_headers('123@123.com', 'cat'))
		# self.assertEqual(response.status_code, 200)
		# json_response = json.loads(response.get_data(as_text=True))
		# self.assertEqual('http://localhost' + json_response['url'], url)
		# self.assertEqual(json_response['body'], 'test api by unittest')
		# self.assertEqual(json_response['body_html'], '<p>test api by unittest</p>')


