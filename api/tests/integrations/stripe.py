from rest_framework.test import APITestCase

from api import models as api_models


class StripeSynchronization(APITestCase):

    def test_new_item_variant_creates_stripe_product(self):
        pass