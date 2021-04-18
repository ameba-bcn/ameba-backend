from unittest import mock

from rest_framework import status
from django.core import signing
from django.contrib.auth import get_user_model

from api.tests._helpers import BaseTest
from api.signals import emails

User = get_user_model()


class TestRecoveryFlow(BaseTest):
    LIST_ENDPOINT = '/api/recovery/'

    @mock.patch.object(emails.PasswordResetRequestEmail, "from_request")
    def test_recovery_request(self, from_request_mock):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        user.activate()

        data = dict(email=user.email)
        response = self._list(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIs(type(response.data['detail']), str)
        from_request_mock.assert_called()

    @mock.patch.object(emails.PasswordResetRequestEmail, "from_request")
    def test_recovery_request_non_existent_user(self, from_request_mock):
        data = dict(email='username@ameba.cat')
        response = self._list(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIs(type(response.data['detail']), str)
        from_request_mock.assert_not_called()

    @mock.patch.object(emails.PasswordChangedEmail, "from_request")
    def test_recovery_token_returns_200(self, from_request_mock):
        user = User.objects.create(
            password='whatever',
            username='UserName',
            email='username@ameba.cat'
        )
        self.assertFalse(user.is_active)
        token = user.get_recovery_token()
        data = dict(token=token, password='wh4tever')
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        from_request_mock.assert_called()

    def test_recovery_token_twice_returns_400(self):
        user = User.objects.create(
            password='whatever',
            username='UserName',
            email='username@ameba.cat'
        )
        user.activate()
        token = user.get_recovery_token()
        data = dict(token=token, password='wh4tever')
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch.object(emails.PasswordChangedEmail, "from_request")
    @mock.patch.object(signing, 'loads')
    def test_recovery_expired_token_returns_400(self, loads_mock,
                                                from_request_mock):
        loads_mock.side_effect = signing.SignatureExpired
        user = User.objects.create(
            password='whatever',
            username='UserName',
            email='username@ameba.cat'
        )
        self.assertFalse(user.is_active)
        token = user.get_recovery_token()
        data = dict(token=token, password='wh4tever')
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        from_request_mock.assert_not_called()

    @mock.patch.object(emails.PasswordChangedEmail, "from_request")
    def test_recovery_changed_token_returns_400(self, from_request_mock):
        user = User.objects.create(
            password='whatever',
            username='UserName',
            email='username@ameba.cat'
        )
        token = user.get_recovery_token()
        if token[0] != 'a':
            token = 'a' + token[1:]
        else:
            token = 'A' + token[1:]

        data = dict(token=token, password='wh4tever')
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        from_request_mock.assert_not_called()

    @mock.patch.object(emails.PasswordChangedEmail, "from_request")
    def test_recovery_empty_token_returns_404(self, from_request_mock):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        self.assertFalse(user.is_active)
        data = dict(token='', password='wh4tever')
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        from_request_mock.assert_not_called()

    @mock.patch.object(emails.PasswordChangedEmail, "from_request")
    def test_recovery_missing_token_returns_400(self, from_request_mock):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        self.assertFalse(user.is_active)
        data = dict(password='wh4tever')
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        from_request_mock.assert_not_called()

    @mock.patch.object(emails.PasswordChangedEmail, "from_request")
    def test_recovery_missing_password_returns_400(self, from_request_mock):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        self.assertFalse(user.is_active)
        token = user.get_recovery_token()
        data = dict(token=token)
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        from_request_mock.assert_not_called()

    @mock.patch.object(emails.PasswordChangedEmail, "from_request")
    def test_recovery_missing_user_returns_404(self, from_request_mock):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        token = user.get_recovery_token()
        user.delete()
        response = self._create(props=dict(token=token), token=None)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        from_request_mock.assert_not_called()
