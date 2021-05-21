import hmac
import hashlib
from unittest import mock
from django.test import tag
from rest_framework import status
from django.conf import settings
from rest_framework.test import APITestCase

import datetime
from api.tests._helpers import BaseTest
from api.models import Subscriber, MailingList
from api import mailgun


def get_signature():
    ep = datetime.datetime(1970, 1, 1, 0, 0, 0)
    timestamp = int((datetime.datetime.utcnow() - ep).total_seconds())
    tok = '12d3bc2438ce9eb0986832957204c63fab66f6c7266132219c'
    signature = hmac.new(
        key=settings.MG_TRACKING_KEY.encode(),
        msg=('{}{}'.format(timestamp, tok)).encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    return {
        'signature': signature,
        'token': tok,
        'timestamp': timestamp
    }


class ApiMailgunUnsubscriptionTest(BaseTest):
    LIST_ENDPOINT = '/api/mailgun_unsubscribe/'

    @tag("unsubscribe")
    @mock.patch('api.mailgun.remove_member')
    def test_existing_email_unsubscribes(self, remove_member_mock):
        email = 'patient1@jacoti.com'
        subscriber = Subscriber.objects.create(email=email)
        mailing_list, created = MailingList.objects.get_or_create(
            address=settings.DEFAULT_MAILING_LIST
        )
        subscriber.mailing_lists.add(mailing_list)
        signature = get_signature()
        event_data = {
            "recipient": email,
            "event": "unsubscribed",
            "mailing-list": {
                "address": settings.DEFAULT_MAILING_LIST
            }
        }
        request_body = {"signature": signature, "event-data": event_data}
        response = self._create(props=request_body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(subscriber.mailing_lists.all())
        remove_member_mock.assert_called_with(
            email=email, list_address=settings.DEFAULT_MAILING_LIST
        )

    @tag("unsubscribe")
    @mock.patch('api.mailgun.remove_member')
    def test_unsubscribe_from_non_existing_address(self, remove_member_mock):
        email = 'patient1@jacoti.com'
        subscriber = Subscriber.objects.create(email=email)
        mailing_list, created = MailingList.objects.get_or_create(
            address=settings.DEFAULT_MAILING_LIST
        )
        subscriber.mailing_lists.add(mailing_list)
        signature = get_signature()
        event_data = {
            "recipient": email,
            "event": "unsubscribed",
            "mailing-list": {
                "address": 'newlett@mail-out.ameba.cat'
            }
        }
        request_body = {"signature": signature, "event-data": event_data}
        response = self._create(props=request_body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(subscriber.mailing_lists.all())
        remove_member_mock.assert_not_called()

    @tag("unsubscribe")
    @mock.patch('api.mailgun.remove_member')
    def test_unsubscribe_other_event_dont_unsubscribe(
        self, remove_member_mock
    ):
        email = 'patient1@jacoti.com'
        subscriber = Subscriber.objects.create(email=email)
        mailing_list, created = MailingList.objects.get_or_create(
            address=settings.DEFAULT_MAILING_LIST
        )
        subscriber.mailing_lists.add(mailing_list)
        signature = get_signature()
        event_data = {
            "recipient": email,
            "event": "other_event",
            "mailing-list": {
                "address": settings.DEFAULT_MAILING_LIST
            }
        }
        request_body = {"signature": signature, "event-data": event_data}
        response = self._create(props=request_body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(subscriber.mailing_lists.all())
        remove_member_mock.assert_not_called()
