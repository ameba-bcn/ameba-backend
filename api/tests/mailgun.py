from unittest import mock
from django.conf import settings

from api.tests._helpers import BaseTest
from api import mailgun
from api.models import MailingList


class TestMailgunApi(BaseTest):

    @mock.patch('api.mailgun.perform_request')
    def test_send_unsubscribe_mail_to_default_list(self, perform_request_mock):
        call_count = perform_request_mock.call_count
        MailingList.objects.create(address=settings.DEFAULT_MAILING_LIST,
                                   is_test=False)
        mailgun.send_unsubscribe_mail_to_mailing_list(
            list_address=settings.DEFAULT_MAILING_LIST
        )
        self.assertEqual(call_count + 1, perform_request_mock.call_count)

    @mock.patch('api.mailgun.perform_request')
    def test_send_unsubscribe_mail_to_test_list(self, perform_request_mock):
        call_count = perform_request_mock.call_count
        address = 'new_mailing_list@mail-out.ameba.cat'
        MailingList.objects.create(address=address)

        mailgun.send_unsubscribe_mail_to_mailing_list(list_address=address)
        self.assertEqual(call_count + 1, perform_request_mock.call_count)
