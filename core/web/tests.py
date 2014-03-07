from core.tests.base import RealizeTest
from core.tests.factories import UserFactory
from flask import url_for
import json

class AuthTest(RealizeTest):
    def get_data_and_status(self, url_name):
        url = url_for(url_name)
        resp = self.client.get(url)
        data = resp.get_data()
        status = resp.status_code
        return json.loads(data), status

    def post_data(self, url_name, data, headers=None):
        url = url_for(url_name)
        resp = self.client.post(url, data=data, headers=headers)
        return json.loads(resp.get_data()), resp.status_code

    def test_register(self):
        url_name = "auth_views.register"
        get_data, status = self.get_data_and_status(url_name)
        self.assertEqual(status, 200)
        self.assertTrue('csrf_token' in get_data)

        token = get_data['csrf_token']

        user_data =  {'email': 'test@realize.pe', 'password': 'testtest'}
        data, status = self.post_data(url_name, user_data)
        self.assertEqual(status, 400)

        data, status = self.post_data(url_name, user_data, {'X-CSRF-Token': token})
        self.assertEqual(status, 201)

    def test_login(self):
        url_name = "auth_views.login"
        get_data, status = self.get_data_and_status(url_name)

        token = get_data['csrf_token']
        user_data = {'email': 'test@realize.pe', 'password': 'testtest'}

        headers = {'X-CSRF-Token': token}
        data, status = self.post_data(url_name, user_data, headers)
        self.assertEqual(status, 400)

        u = UserFactory(email='test@realize.pe')
