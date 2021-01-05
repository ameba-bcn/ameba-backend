from api.tests._helpers import BaseTest
from django.core.files.images import ImageFile
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList
from dateutil import parser
from django.test import tag

from api import models
from api.models.interview import INTRO_PREVIEW


def valid_date(date_text):
    parser.parse(date_text)
    return True


def valid_url(url_text):
    return url_text.startswith('http')


class TestCart(BaseTest):

    def test_discounts_applied_after_save(self):
        pass