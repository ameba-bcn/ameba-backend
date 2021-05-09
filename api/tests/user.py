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
        user.activate()
        refresh = RefreshToken.for_user(user)
        return user, refresh.access_token

    def _check_is_user(self, expected, response_data):
        self.assertIn('username', response_data)
        self.assertIn('email', response_data)
        self.assertIn('date_joined', response_data)
        self.assertIn('member', response_data)

        self.assertEqual(response_data['username'], expected['username'])
        self.assertEqual(response_data['email'], expected['email'])
        self.assertIs(response_data['member'], expected['member'])

    def get_profile(self, pk, token):
        self._authenticate(token)
        return self.client.get(f'/api/users/{pk}/member_profile/')

    def update_profile(self, pk, token, props):
        self._authenticate(token)
        return self.client.patch(f'/api/users/{pk}/member_profile/',data=props)

    def post_profile(self, pk, token, props):
        self._authenticate(token)
        return self.client.post(f'/api/users/{pk}/member_profile/',data=props)


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
            'date_joined': None,
            'member': None
        }

        resp_data = dict(self._create(user_props).data)

        self.assertEqual(len(expected), len(resp_data))

        self.assertIn('username', resp_data)
        self.assertIn('email', resp_data)
        self.assertIn('date_joined', resp_data)
        self.assertIn('member', resp_data)

        self.assertEqual(resp_data['username'], expected['username'])
        self.assertEqual(resp_data['email'], expected['email'])
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

    def test_post_new_user_with_is_active_have_no_effect(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'new_not_active_user@ameba.cat',
            # 'is_active': True
        }
        self._create(user_props)
        user = User.objects.get(email='new_not_active_user@ameba.cat')
        self.assertFalse(user.is_active)

    def test_post_user_member_profile(self):
        user_props = {
            'username': 'User',
            'password': 'ameba12345',
            'email': 'user@ameba.cat',
        }

        user, token = self._insert_user(user_props)
        user.is_active = True
        user.save()

        profile_props = {
            'address': 'My user address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816'
        }

        response = self.post_profile(pk='current', token=token,
                                 props=profile_props)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('number', response.data)

        user.refresh_from_db()
        self.assertTrue(user.member)
        self.assertTrue(Member.objects.filter(user=user))

    def test_get_member_from_current_user(self):
        user_props = {
            'username': 'User',
            'password': 'ameba12345',
            'email': 'user@ameba.cat',
        }

        user, token = self._insert_user(user_props)
        user.is_active = True
        user.save()

        member = Member.objects.create(
            user=user,
            address='Address',
            first_name='First Name',
            last_name='Last Name',
            phone_number='661839816'
        )
        response = self.get_profile(pk=user.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_non_member_from_current_user(self):
        user_props = {
            'username': 'User',
            'password': 'ameba12345',
            'email': 'user@ameba.cat',
        }

        user, token = self._insert_user(user_props)
        user.is_active = True
        user.save()

        response = self.get_profile(pk=user.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_member_from_current_user(self):
        user_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user@ameba.cat',
        }

        user, token = self._insert_user(user_props)
        user.is_active = True
        user.save()

        member = Member.objects.create(
            user=user,
            address='Address',
            first_name='First Name',
            last_name='Last Name',
            phone_number='654321987'
        )
        response = self.update_profile(
            pk=user.id, token=token, props={'phone_number': '666555444'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '666555444')
