from core.tests.base import RealizeTest
from core.tests.factories import UserFactory
from core.database.models import User
from flask import url_for
import json

class WebTest(RealizeTest):

    def get_csrf_headers(self, url_name):
        get_data, status = self.get_data(url_name)
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
        return data['user']

    def send_data(self, method, url_name, data, headers=None, **kwargs):
        url = url_for(url_name, **kwargs)
        func = getattr(self.client, method)
        resp = func(url, data=json.dumps(data), headers=headers, content_type="application/json")
        return json.loads(resp.get_data()), resp.status_code

    def post_data(self, url_name, data, headers=None, **kwargs):
        return self.send_data("post", url_name, data, headers, **kwargs)

    def put_data(self, url_name, data, headers=None, **kwargs):
        return self.send_data("put", url_name, data, headers, **kwargs)

    def patch_data(self, url_name, data, headers=None, **kwargs):
        return self.send_data("post", url_name, data, headers, **kwargs)

    def get_data(self, url_name, **kwargs):
        url = url_for(url_name, **kwargs)
        resp = self.client.get(url, content_type="application/json")
        data = resp.get_data()
        status = resp.status_code
        return json.loads(data), status

    def create_group(self):
        url_name = "group_views.groupview"
        group_data = {'name': 'Test', 'description': 'Test group.'}
        data, status = self.post_data(url_name, group_data)
        return data

class AuthTest(WebTest):

    def test_register(self):
        url_name = "auth_views.register"
        get_data, status = self.get_data(url_name)
        self.assertEqual(status, 200)
        self.assertTrue('csrf_token' in get_data)

        token = get_data['csrf_token']

        user_data = {'email': 'test@realize.pe', 'password': 'testtest'}
        data, status = self.post_data(url_name, user_data, {'X-CSRF-Token': token})
        self.assertEqual(status, 200)

    def test_login(self):
        url_name = "auth_views.login"
        get_data, status = self.get_data(url_name)

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

class UserTest(WebTest):
    def test_profile(self):
        url_name = "user_views.userprofile"
        user_data = self.create_and_login_user()
        profile, status = self.get_data(url_name, hashkey=user_data['hashkey'])
        self.assertEqual(user_data['hashkey'], profile['hashkey'])

        settings = {'test': 'test'}
        timezone = "America/New_York"

        _, status = self.put_data(url_name, {'settings': json.dumps(settings), 'timezone': timezone}, hashkey=user_data['hashkey'])
        self.assertEqual(status, 200)

        profile, status = self.get_data(url_name, hashkey=user_data['hashkey'])
        self.assertEqual(profile['timezone'], timezone)
        profile['settings'] = json.loads(profile['settings'])
        self.assertEqual(profile['settings'], settings)

class GroupTest(WebTest):
    def test_groups(self):
        url_name = "group_views.groupview"
        user_data = self.create_and_login_user()
        group = self.create_group()
        self.assertEqual(group['name'], "Test")

        groups, status = self.get_data(url_name)
        self.assertEqual(len(groups), 1)

    def test_group_detail(self):
        url_name = "group_views.groupdetailview"
        user_data = self.create_and_login_user()
        group = self.create_group()

        group, status = self.get_data(url_name, hashkey=group['hashkey'])
        self.assertEqual(group['name'], "Test")

        put_data = {'description': "Test group desc."}
        group, status = self.put_data(url_name, data=put_data, hashkey=group['hashkey'])
        self.assertEqual(group['description'], put_data['description'])

    def test_user_groups(self):
        url_name = "group_views.usergroupview"
        user_data = self.create_and_login_user()
        group = self.create_group()

        groups, status = self.get_data(url_name, user_hashkey=user_data['hashkey'])
        self.assertEqual(len(groups), 1)

        action_url_name = "group_views.usergroupactionview"
        data, status = self.get_data(action_url_name, user_hashkey=user_data['hashkey'], group_hashkey=group['hashkey'], action="remove")

        groups, status = self.get_data(url_name, user_hashkey=user_data['hashkey'])
        self.assertEqual(len(groups), 0)

        data, status = self.get_data(action_url_name, user_hashkey=user_data['hashkey'], group_hashkey=group['hashkey'], action="add")

        groups, status = self.get_data(url_name, user_hashkey=user_data['hashkey'])
        self.assertEqual(len(groups), 1)


