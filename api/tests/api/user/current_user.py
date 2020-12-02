from django.test import tag
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User


class UserTest(APITestCase):

    def _get_current_user(self, token):
        endpoint = '/api/users/current/'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))
        return self.client.get(endpoint)

    @tag("current_user")
    def test_get_current_user(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat',
            'is_active': True
        }
        expected = {
            'username': user_props.get('username'),
            'email': user_props.get('email'),
            'is_active': True,
            'date_joined': None,
            'member': None
        }

        user = User(**user_props)
        user.save()

        refresh = RefreshToken.for_user(user)
        response = self._get_current_user(refresh.access_token)
        resp_data = dict(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(expected), len(resp_data))

        self.assertIn('username', resp_data)
        self.assertIn('email', resp_data)
        self.assertIn('is_active', resp_data)
        self.assertIn('date_joined', resp_data)
        self.assertIn('member', resp_data)

        self.assertEqual(resp_data['username'], expected['username'])
        self.assertEqual(resp_data['email'], expected['email'])
        self.assertIs(resp_data['is_active'], expected['is_active'])
        self.assertIs(resp_data['member'], expected['member'])
