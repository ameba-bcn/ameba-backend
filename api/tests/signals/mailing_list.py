from unittest import mock
from django.conf import settings

from rest_framework import status
from django.contrib.auth import get_user_model

from api.tests._helpers import BaseTest
from api.models import MailingList
from api.models.mailing_list import DeletionNotAllowed

User = get_user_model()


class MailingListSignals(BaseTest):
    LIST_ENDPOINT = '/api/subscribe/'

    @mock.patch('api.mailgun.post_mailing_list')
    def test_new_mailing_list_synchronized(self, post_mailing_list_mock):
        MailingList.objects.create(
            address='new_mailing_list@mail-out.ameba.cat'
        )
        post_mailing_list_mock.assert_called_with(
            list_address='new_mailing_list@mail-out.ameba.cat'
        )

    @mock.patch('api.mailgun.delete_mailing_list')
    def test_del_mailing_list_synchronized(self, del_mailing_list_mock):
        mailing_list = MailingList.objects.create(
            address='new_mailing_list@mail-out.ameba.cat'
        )
        mailing_list.delete()
        del_mailing_list_mock.assert_called_with(
            list_address='new_mailing_list@mail-out.ameba.cat'
        )

    @mock.patch('api.mailgun.delete_mailing_list')
    def test_del_default_list_not_allowed(self, del_mailing_list_mock):
        mailing_list = MailingList.objects.create(
            address=settings.DEFAULT_MAILING_LIST
        )

        def delete_mailing_list():
            mailing_list.delete()

        self.assertRaises(DeletionNotAllowed, delete_mailing_list)
        del_mailing_list_mock.assert_not_called()
