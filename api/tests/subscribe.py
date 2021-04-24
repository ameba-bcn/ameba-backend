from unittest import mock

from rest_framework import status
from django.core import signing
from django.contrib.auth import get_user_model

from api.tests._helpers import BaseTest
from api.signals import emails
from api.models import Subscriber

User = get_user_model()


class SubscribeTest(BaseTest):
    LIST_ENDPOINT = '/api/subscribe/'

    def test_subscribe_new_email(self):
        data = dict(email='new@email.si')
        response = self._create(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscriber.objects.filter(email='new@email.si'))

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
