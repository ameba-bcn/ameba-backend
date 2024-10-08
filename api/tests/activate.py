from unittest import mock

from rest_framework import status
from django.core import signing
from django.contrib.auth import get_user_model

from api.tests._helpers import BaseTest

User = get_user_model()


class TestActivation(BaseTest):
    LIST_ENDPOINT = '/api/activate/'

    def test_activate_mechanism(self):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        self.assertFalse(user.is_active)
        token = user.get_activation_token()

        data = dict(token=token)
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIs(type(response.data['detail']), str)

    @mock.patch.object(signing, 'loads')
    def test_activate_expired_token_returns_400(self, loads_mock):
        loads_mock.side_effect = signing.SignatureExpired
        user = User.objects.create(
            password='whatever',
            username='UserName',
            email='username@ameba.cat'
        )
        self.assertFalse(user.is_active)
        token = user.get_activation_token()
        data = dict(token=token)
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_changed_token_returns_400(self):
        user = User.objects.create(
            password='whatever',
            username='UserName',
            email='username@ameba.cat'
        )
        token = user.get_activation_token()
        if token[0] != 'a':
            token = 'a' + token[1:]
        else:
            token = 'A' + token[1:]

        data = dict(token=token)
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_empty_token_returns_404(self):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        self.assertFalse(user.is_active)
        data = dict(token='')
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_missing_token_returns_400(self):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        self.assertFalse(user.is_active)
        response = self._create(props={}, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_missing_user_returns_404(self):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        token = user.get_activation_token()
        user.delete()
        response = self._create(props=dict(token=token), token=None)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
