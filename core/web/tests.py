from core.tests.base import RealizeTest
from core.tests.factories import UserFactory
from core.database.models import User
from flask import url_for
import json

class WebTest(RealizeTest):

    def get_csrf_headers(self, url_name):
        get_data, status = self.get_data_and_status(url_name)
        token = get_data['csrf_token']
        headers = {'X-CSRF-Token': token}
        return headers

    def create_and_login_user(self):
        url_name = "auth_views.login"
        headers = self.get_csrf_headers(url_name)
        u = UserFactory(email='test@realize.pe')
        u.password = "testtest"
        user_data = {'email': 'test@realize.pe', 'password': 'testtest'}
        data, status = self.post_data(url_name, user_data, headers)
        print data
        return data['user']

    def post_data(self, url_name, data, headers=None, **kwargs):
        url = url_for(url_name, **kwargs)
        resp = self.client.post(url, data=data, headers=headers)
        return json.loads(resp.get_data()), resp.status_code

class AuthTest(WebTest):
    def get_data_and_status(self, url_name):
        url = url_for(url_name)
        resp = self.client.get(url)
        data = resp.get_data()
        status = resp.status_code
        return json.loads(data), status

    def test_register(self):
        url_name = "auth_views.register"
        get_data, status = self.get_data_and_status(url_name)
        self.assertEqual(status, 200)
        self.assertTrue('csrf_token' in get_data)

        token = get_data['csrf_token']

        user_data =  {'email': 'test@realize.pe', 'password': 'testtest'}
        data, status = self.post_data(url_name, user_data, {'X-CSRF-Token': token})
        self.assertEqual(status, 200)

    def test_login(self):
        url_name = "auth_views.login"
        get_data, status = self.get_data_and_status(url_name)

        token = get_data['csrf_token']
        user_data = {'email': 'test@realize.pe', 'password': 'testtest'}

        headers = {'X-CSRF-Token': token}
        data, status = self.post_data(url_name, user_data, headers)
        self.assertEqual(status, 400)

        user_data = self.create_and_login_user()

        self.assertTrue('hashkey' in user_data and 'token' in user_data)

    def test_auth_check(self):
        url_name = "auth_views.authenticationcheck"
        user_data = self.create_and_login_user()
        data, status = self.post_data(url_name, user_data)
        self.assertEqual(status, 200)