from django.test import tag
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.utils.serializer_helpers import ReturnList

from api.models import User


class UserTest(APITestCase):
    endpoint = '/api/users/current/'

    def _get_current_user(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))
        return self.client.get(self.endpoint)

    def _partial_update_current_user(self, token, props):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))
        return self.client.patch(self.endpoint, data=props)

    def _update_current_user(self, token, props):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))
        return self.client.put(self.endpoint, data=props)

    def _delete_current_user(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))
        return self.client.delete(self.endpoint)

    def _list_users(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))
        endpoint = '/api/users/'
        return self.client.get(endpoint)

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

    @tag("current_user")
    def test_update_current_user(self):
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

        new_props = {
            'username': 'Juanito DJ'
        }

        response = self._partial_update_current_user(refresh.access_token, new_props)
        resp_data = dict(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(expected), len(resp_data))

        self.assertIn('username', resp_data)
        self.assertIn('email', resp_data)
        self.assertIn('is_active', resp_data)
        self.assertIn('date_joined', resp_data)
        self.assertIn('member', resp_data)

        self.assertEqual(resp_data['username'], new_props['username'])
        self.assertEqual(resp_data['email'], expected['email'])
        self.assertIs(resp_data['is_active'], expected['is_active'])
        self.assertIs(resp_data['member'], expected['member'])

    def test_updated_password_is_hashed(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat',
            'is_active': True
        }

        user, access = self._insert_user(user_props)
        old_pass = user.password

        new_props = {'password': 'MyNewPassword'}
        response = self._partial_update_current_user(access, new_props)
        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(user.check_password(user_props['password']))
        self.assertTrue(user.check_password(new_props['password']))

    def test_updated_duplicated_email_raises_exception(self):
        user_a_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat',
            'is_active': True
        }
        user_b_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser2@ameba.cat',
            'is_active': True
        }

        self._insert_user(user_a_props)
        user_b, access_b = self._insert_user(user_b_props)

        new_props = {'email': 'amebauser1@ameba.cat'}
        response = self._partial_update_current_user(access_b, new_props)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        user, access_token = self._insert_user(user_props)
        response = self._get_current_user(access_token)
        resp_data = dict(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(expected), len(resp_data))
        self._check_is_user(expected, resp_data)

    @tag("current_user")
    def test_delete_current_user(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat',
            'is_active': True
        }

        user = User(**user_props)
        user.save()

        refresh = RefreshToken.for_user(user)
        response = self._delete_current_user(refresh.access_token)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email=user.email).exists())

    @tag("current_user")
    def test_current_user_doesnt_accept_update(self):
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
        response = self._update_current_user(access_token, update_props)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

    @tag("current_user")
    def test_current_user_only_have_access_to_himself(self):
        user_a_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat',
            'is_active': True
        }
        current_user_props = {
            'username': 'Current User',
            'password': 'MyPassword',
            'email': 'currentuser@ameba.cat',
            'is_active': True
        }
        expected_user_props = {
            'username': 'Current User',
            'member': None,
            'email': 'currentuser@ameba.cat',
            'is_active': True
        }

        self._insert_user(user_a_props)
        cur_user, access_token = self._insert_user(current_user_props)
        response = self._list_users(access_token)
        resp_data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(type(resp_data), ReturnList)
        self.assertEqual(len(response.data), 1)
        self._check_is_user(expected_user_props, resp_data)
