import datetime
import pytz

from django.test import tag
from rest_framework.test import APITestCase
from rest_framework import status

from api.models import User


class UserTest(APITestCase):

    def _create_user(self, user_props):
        endpoint = '/api/users/'
        return self.client.post(endpoint, user_props)

    @tag("user")
    def test_create_user(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        response = self._create_user(user_props)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=user_props['email']).exists())

    def test_create_not_member_user_returns_expected(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }

        expected = {
            'username': user_props.get('username'),
            'email': user_props.get('email'),
            'is_active': False,
            'date_joined': None,
            'member': None
        }

        resp_data = dict(self._create_user(user_props).data)

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

    def test_create_user_writes_proper_datetime(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        utc = pytz.UTC
        max_datetime = datetime.datetime.now() + datetime.timedelta(seconds=2)
        max_datetime = max_datetime.replace(tzinfo=utc)
        self._create_user(user_props)
        user = User.objects.get(email=user_props['email'])
        date_joined = user.date_joined.replace(tzinfo=utc)
        self.assertLess(date_joined,  max_datetime)

    def test_create_user_hashes_password(self):
        self.assertFalse(True)
