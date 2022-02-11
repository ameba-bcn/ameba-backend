from unittest import mock
from django.conf import settings

from rest_framework import status
from django.contrib.auth import get_user_model

from api.tests._helpers import BaseTest
from api.models import Subscriber
from api import email_factories

User = get_user_model()


class SubscribeTest(BaseTest):
    LIST_ENDPOINT = '/api/subscribe/'

    @mock.patch('api.mailgun.add_member')
    def test_subscribe_new_email(self, add_member_mock, send_to):
        data = dict(email='new@email.si')
        response = self._create(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscriber.objects.filter(email='new@email.si'))
        subscriber = Subscriber.objects.get(email='new@email.si')
        self.assertEqual(
            subscriber.mailing_lists.first().address,
            settings.DEFAULT_MAILING_LIST
        )
        add_member_mock.assert_called_with(
            email=data['email'],
            list_address=settings.DEFAULT_MAILING_LIST
        )

    def test_subscribe_same_email(self):
        data = dict(email='new@email.si')
        self._create(data)
        response = self._create(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscriber.objects.filter(email='new@email.si'))

    def test_subscribe_wrong_email(self):
        data = dict(email='newemail.si')
        self._create(data)
        response = self._create(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Subscriber.objects.filter(email='new@email.si'))

    def test_subscribe_empty_email(self):
        data = dict(email='')
        self._create(data)
        response = self._create(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_no_email(self):
        data = dict()
        self._create(data)
        response = self._create(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
