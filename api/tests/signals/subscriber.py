from unittest import mock

from api.tests._helpers import BaseTest
from api.models import MailingList, Subscriber


class SubscriberSignalsTest(BaseTest):

    @mock.patch('api.mailgun.add_member')
    def test_new_subscription_gets_synced(self, add_member_mock):
        email = 'user@email.com'
        address = 'new_mailing_list@mail-out.ameba.cat'
        mailing_list = MailingList.objects.create(address=address)
        subscriber = Subscriber.objects.create(email=email)
        subscriber.mailing_lists.add(mailing_list)
        add_member_mock.assert_called_with(email=email, list_address=address)

    @mock.patch('api.mailgun.remove_member')
    def test_unsubscription_gets_synced(self, remove_member_mock):
        email = 'user@email.com'
        address = 'new_mailing_list@mail-out.ameba.cat'
        mailing_list = MailingList.objects.create(address=address)
        subscriber = Subscriber.objects.create(email=email)
        subscriber.mailing_lists.add(mailing_list)
        subscriber.mailing_lists.remove(mailing_list)
        remove_member_mock.assert_called_with(email=email,list_address=address)
