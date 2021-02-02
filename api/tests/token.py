from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import tag

from api.tests import _helpers
from api import models


class TestSessions(_helpers.BaseTest):
    LIST_ENDPOINT = '/api/token/'

    def login(self, email, password):
        props = {'email': email, 'password': password}
        return self._create(props)

    def delete(self, token='', attrs=None):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(token)
        )
        return self.client.delete(self.LIST_ENDPOINT, data=attrs)

    @staticmethod
    def get_token(user):
        return RefreshToken.for_user(user)

    @staticmethod
    def create_user(email, password):
        username = email.split('@')[0]
        props = {'email': email, 'password': password, 'username': username}
        user = models.User.objects.create(**props)
        user.activate()
        return user

    @tag("token")
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

    @tag("token")
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
        self.assertEqual(
            response.data['detail'],
            'No active account found with the given credentials'
        )
        self.assertEqual(list(response.data.keys()), ['detail'])

    @tag("token")
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
        self.assertEqual(
            response.data['detail'],
            'No active account found with the given credentials'
        )
        self.assertEqual(list(response.data.keys()), ['detail'])

    @tag("token")
    def test_delete_token_authenticated(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        user = self.create_user(**user_attrs)
        response = self.login(**user_attrs)
        token = self.get_token(user)
        attrs = {'refresh': str(token)}
        response = self.delete(token.access_token, attrs=attrs)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @tag("token")
    def test_delete_token_unauthenticated(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        user = self.create_user(**user_attrs)
        token = self.get_token(user)
        attrs = {'refresh': str(token)}
        response = self.login(**user_attrs)
        response = self.delete(attrs={'refresh': str(token)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @tag("token")
    def test_deleted_token_does_not_work_anymore(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        user = self.create_user(**user_attrs)
        response = self.login(**user_attrs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = self.get_token(user)
        attrs = {'refresh': str(token)}
        self.delete(token.access_token, attrs=attrs)
        response = self.delete(token.access_token, attrs=attrs)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
