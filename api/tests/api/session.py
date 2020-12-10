from rest_framework import status

from api.tests.api import api_test_helpers
from api import models


class TestSessions(api_test_helpers.BaseTest):
    LIST_ENDPOINT = '/api/token/'

    def login(self, email, password):
        props = {'email': email, 'password': password}
        return self._create(props)

    def create_user(self, email, password):
        username = email.split('@')[0]
        props = {'email': email, 'password': password, 'username': username}
        user = models.User.objects.create(**props)
        return user

    def test_user_login(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        self.create_user(**user_attrs)
        response = self.login(**user_attrs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_wrong_password_user_login(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        self.create_user(**user_attrs)
        wrong_cred = {
            'email': 'user@ameba.cat',
            'password': 'mypasswordss'
        }
        response = self.login(**wrong_cred)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_email_user_login_does_not_give_info(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        self.create_user(**user_attrs)
        wrong_cred = {
            'email': 'user@amebass.cat',
            'password': 'mypassword'
        }
        response = self.login(**wrong_cred)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
