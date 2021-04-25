from unittest import mock
from django.conf import settings

from api.tests._helpers import BaseTest
from api import mailgun
from api.models import MailingList


class MailgunApiTest(BaseTest):

    @mock.patch('api.mailgun.perform_request')
    def test_send_unsubscribe_mail_to_default_list(self, perform_request_mock):
        mailgun.send_unsubscribe_mail_to_mailing_list(
            list_address=settings.DEFAULT_MAILING_LIST
        )
        perform_request_mock.assert_not_called()

    @mock.patch('api.mailgun.perform_request')
    def test_send_unsubscribe_mail_to_test_list(self, perform_request_mock):
        address = 'new_mailing_list@mail-out.ameba.cat'
        MailingList.objects.create(address=address)

        mailgun.send_unsubscribe_mail_to_mailing_list(list_address=address)
        perform_request_mock.assert_called()
