import datetime
import pytz

from django.test import tag
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User, Member
from api.tests import _helpers


class BaseUserTest(_helpers.BaseTest):
    DETAIL_ENDPOINT = '/api/users/{pk}/'
    LIST_ENDPOINT = '/api/users/'

    @staticmethod
    def _insert_user(props):
        user = User.objects.create_user(**props)
        refresh = RefreshToken.for_user(user)
        return user, refresh.access_token

    def _check_is_user(self, expected, response_data):
        self.assertIn('username', response_data)
        self.assertIn('email', response_data)
        self.assertIn('is_active', response_data)
        self.assertIn('date_joined', response_data)
        self.assertIn('member', response_data)

        self.assertEqual(response_data['username'], expected['username'])
        self.assertEqual(response_data['email'], expected['email'])
        self.assertIs(response_data['is_active'], expected['is_active'])
        self.assertIs(response_data['member'], expected['member'])


class UserTest(BaseUserTest):

    @tag("user")
    def test_create_user(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        response = self._create(user_props)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=user_props['email']).exists())

    @tag("user")
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

        resp_data = dict(self._create(user_props).data)

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

    @tag("user")
    def test_create_user_writes_proper_datetime(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        utc = pytz.UTC
        max_datetime = datetime.datetime.now() + datetime.timedelta(seconds=2)
        max_datetime = max_datetime.replace(tzinfo=utc)
        self._create(user_props)
        user = User.objects.get(email=user_props['email'])
        date_joined = user.date_joined.replace(tzinfo=utc)
        self.assertLess(date_joined,  max_datetime)

    @tag("user")
    def test_create_user_hashes_password(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        response = self._create(user_props)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=user_props['email'])
        self.assertTrue(user.check_password(user_props['password']))
        self.assertTrue(user._is_password_hashed())

    @tag("user")
    def test_create_user_matching_member_returns_member(self):
        member_data = {
            'number':  1,
            'email':  'amebauser1@ameba.cat',
            'first_name': 'Amen',
            'last_name': 'Bauser',
            'phone_number': '1238746'
        }
        member = Member.objects.create(**member_data)

        user_props = {
            'username': 'AmebaUser',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }

        expected = {
            'username': user_props.get('username'),
            'email': user_props.get('email'),
            'is_active': False,
            'date_joined': None,
            'member': 1
        }

        resp_data = dict(self._create(user_props).data)

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

    @tag("user")
    def test_get_user_not_authenticated(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat',
            'is_active': True
        }
        user, access_token = self._insert_user(user_props)
        response = self._get(pk=user.pk, token='')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @tag("user")
    def test_update_user_not_authenticated(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat',
            'is_active': True
        }
        update_props = {
            'username': 'Other username',
            'password': 'OtherPassword',
            'email': 'othermail@ameba.cat',
            'is_active': True
        }
        user, access_token = self._insert_user(user_props)
        response = self._update(pk=user.pk, token=None, props=update_props)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )
