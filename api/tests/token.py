import rest_framework.status as status
import rest_framework_simplejwt.tokens as tokens
import django.test as django_test

import api.tests._helpers as helpers
import api.models as api_models
import api.exceptions as api_exceptions


class TestSessions(helpers.BaseTest):
    LIST_ENDPOINT = '/api/token/'
    DETAIL_ENDPOINT = '/api/token/{id}/'
    REFRESH_ENDPOINT = '/api/token/refresh/'

    def login(self, email, password):
        props = {'email': email, 'password': password}
        return self._create(props)

    def refresh(self, refresh_token=''):
        props = dict(refresh=refresh_token)
        return self.client.post(self.REFRESH_ENDPOINT, data=props, follow=True)

    def delete(self, pk, token=''):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(token)
        )
        return self.client.delete(self.DETAIL_ENDPOINT.format(id=pk),
                                  follow=True)

    @staticmethod
    def get_token(user):
        return tokens.RefreshToken.for_user(user)

    @staticmethod
    def create_user(email, password):
        username = email.split('@')[0]
        props = {'email': email, 'password': password, 'username': username}
        user = api_models.User.objects.create(**props)
        user.activate()
        return user

    @django_test.tag("token")
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

    @django_test.tag("token")
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
        self.assertEqual(list(response.data.keys()), ['detail'])

    @django_test.tag("token")
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
            api_exceptions.WrongProvidedCredentials.default_detail
        )
        self.assertEqual(list(response.data.keys()), ['detail'])

    @django_test.tag("token")
    def test_delete_token_authenticated(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        user = self.create_user(**user_attrs)
        self.login(**user_attrs)
        token = self.get_token(user)
        response = self.delete(token, token.access_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @django_test.tag("token")
    def test_delete_token_unauthenticated(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        user = self.create_user(**user_attrs)
        token = self.get_token(user)
        self.login(**user_attrs)
        response = self.delete(pk=token)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @django_test.tag("token")
    def test_deleted_token_does_not_work_anymore(self):
        user_attrs = {
            'email': 'user@ameba.cat',
            'password': 'mypassword'
        }
        user = self.create_user(**user_attrs)
        response = self.login(**user_attrs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = self.get_token(user)
        self.delete(token, token.access_token)
        response = self.delete(token, token.access_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_returns_new_token(self):
        user_attrs = {
            'email': 'new_user@ameba.cat',
            'password': 'ameba12345'
        }
        self.create_user(**user_attrs)
        response = self.login(**user_attrs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        access = response.data['access']
        refresh = response.data['refresh']

        response = self.refresh(refresh)

        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['access'], access)
