from unittest import mock
from django.conf import settings

from api.tests._helpers import BaseTest
from api.models import Subscriber, User


class SubscriberSignalsTest(BaseTest):

    def test_new_user_gets_subscribed(self):
        email = 'user@email.com'

        self.assertFalse(Subscriber.objects.filter(email=email))

        User.objects.create(
            email=email, username='user', password='12345'
        )

        self.assertTrue(Subscriber.objects.filter(email=email))
        subscriber = Subscriber.objects.get(email=email)
        self.assertTrue(subscriber.mailing_lists.filter(
            address=settings.DEFAULT_MAILING_LIST)
        )

    def test_removed_user_gets_unsubscribed(self):
        email = 'user@email.com'
        self.assertFalse(Subscriber.objects.filter(email=email))
        user = User.objects.create(
            email=email, username='user', password='12345'
        )
        self.assertTrue(Subscriber.objects.filter(email=email))
        user.delete()
        self.assertFalse(Subscriber.objects.filter(email=email))
