from django.test import tag
from rest_framework import status

from api.tests.user import BaseUserTest


class CurrentUserTest(BaseUserTest):

    def _get_current_user(self, token):
        return self._get('current', token)

    def _partial_update_current_user(self, token, props):
        return self._partial_update('current', token, props)

    def _update_current_user(self, token, props):
        return self._update('current', token, props)

    def _delete_current_user(self, token):
        return self._delete('current', token)

    @tag("current_user")
    def test_update_current_user(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        expected = {
            'username': user_props.get('username'),
            'email': user_props.get('email'),
            'date_joined': None,
            'language': None,
            'member': None
        }

        user, access_token = self._insert_user(user_props)
        new_props = {
            'username': 'Juanito DJ'
        }

        response = self._partial_update_current_user(access_token, new_props)
        resp_data = dict(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(expected), len(resp_data))

        self.assertIn('username', resp_data)
        self.assertIn('email', resp_data)
        self.assertIn('date_joined', resp_data)
        self.assertIn('member', resp_data)

        self.assertEqual(resp_data['username'], new_props['username'])
        self.assertEqual(resp_data['email'], expected['email'])
        self.assertIs(resp_data['member'], expected['member'])

    # @tag("current_user")
    # def test_updated_password_is_hashed(self):
    #     user_props = {
    #         'username': 'Ameba User',
    #         'password': 'MyPassword',
    #         'email': 'amebauser1@ameba.cat',
    #         'is_active': True
    #     }
    #
    #     user, access = self._insert_user(user_props)
    #
    #     new_props = {'password': 'MyNewPassword'}
    #     response = self._partial_update_current_user(access, new_props)
    #     user.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertFalse(user.check_password(user_props['password']))
    #     self.assertTrue(user.check_password(new_props['password']))

    # @tag("current_user")
    # def test_updated_duplicated_email_raises_exception(self):
    #     user_a_props = {
    #         'username': 'Ameba User',
    #         'password': 'MyPassword',
    #         'email': 'amebauser1@ameba.cat',
    #         'is_active': True
    #     }
    #     user_b_props = {
    #         'username': 'Ameba User',
    #         'password': 'MyPassword',
    #         'email': 'amebauser2@ameba.cat',
    #         'is_active': True
    #     }
    #
    #     self._insert_user(user_a_props)
    #     user_b, access_b = self._insert_user(user_b_props)
    #
    #     new_props = {'email': 'amebauser1@ameba.cat'}
    #     response = self._partial_update_current_user(access_b, new_props)
    #
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @tag("current_user")
    def test_get_current_user(self):
        user_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        expected = {
            'username': user_props.get('username'),
            'email': user_props.get('email'),
            'date_joined': None,
            'language': None,
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

        user, access_token = self._insert_user(user_props)

        response = self._delete_current_user(access_token)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @tag("current_user")
    def test_current_user_can_update(self):
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
            'email': 'amebauser1@ameba.cat'
        }
        current_user_props = {
            'username': 'Current User',
            'password': 'MyPassword',
            'email': 'currentuser@ameba.cat'
        }
        expected_user_props = {
            'username': 'Current User',
            'member': None,
            'email': 'currentuser@ameba.cat'
        }

        other, other_token = self._insert_user(user_a_props)
        cur_user, access_token = self._insert_user(current_user_props)
        response = self._get_current_user(access_token)
        resp_data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_user(expected_user_props, resp_data)

        other_response = self._get(other.pk, access_token)
        self.assertEqual(other_response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("current_user")
    def test_current_user_can_not_delete_other_user(self):
        user_a_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        current_user_props = {
            'username': 'Current User',
            'password': 'MyPassword',
            'email': 'currentuser@ameba.cat'
        }
        user_a, access_token_a = self._insert_user(user_a_props)
        cur_user, access_token = self._insert_user(current_user_props)
        response = self._delete(pk=user_a.pk, token=access_token)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @tag("current_user")
    def test_current_user_can_not_patch_other_user(self):
        user_a_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        current_user_props = {
            'username': 'Current User',
            'password': 'MyPassword',
            'email': 'currentuser@ameba.cat'
        }

        update_props = {
            'username': 'New Currrent User'
        }

        user_a, access_token_a = self._insert_user(user_a_props)
        cur_user, access_token = self._insert_user(current_user_props)
        response = self._partial_update(
            user_a.pk, access_token, update_props
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("current_user")
    def test_current_user_can_not_update_other_user(self):
        user_a_props = {
            'username': 'Ameba User',
            'password': 'MyPassword',
            'email': 'amebauser1@ameba.cat'
        }
        current_user_props = {
            'username': 'Current User',
            'password': 'MyPassword',
            'email': 'currentuser@ameba.cat'
        }

        user_a, access_token_a = self._insert_user(user_a_props)
        cur_user, access_token = self._insert_user(current_user_props)
        response = self._update(
            user_a.pk, access_token, current_user_props
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
