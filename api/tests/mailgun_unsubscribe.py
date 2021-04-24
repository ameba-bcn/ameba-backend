import hmac
import hashlib
from unittest import mock
from django.test import tag
from rest_framework import status
from django.conf import settings
from rest_framework.test import APITestCase

import datetime
from api.tests._helpers import BaseTest
from api.models import Subscriber
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
    LIST_ENDPOINT = 'api/mailgun_unsubscribe/'

    @tag("unsubscribe")
    def test_existing_email_unsubscribes(self):
        email = 'patient1@jacoti.com'
        Subscriber.objects.create(email=email)

        signature = get_signature()
        event_data = {
            'recipient': email,
            'event': 'unsubscribed'
        }
        request_body = {'signature': signature, 'event-data': event_data}
        response = self._create(props=request_body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscriber.objects.filter(email=email))
