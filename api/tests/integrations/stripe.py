from rest_framework.test import APITestCase

from api import stripe
from api import models as api_models
from api.tests.helpers import (
    user as user_helpers,
    items as item_helpers,
    carts as cart_helpers
)


class TestStripeSynchronization(APITestCase):

    def test_new_item_variant_creates_stripe_product(self):
        subs = item_helpers.create_item(
            pk=1,
            name='Socio',
            item_class=api_models.Subscription
        )
        price = 25 * 100
        subs_variant = item_helpers.create_item_variant(
            item=subs,
            price=price,
            stock=-1,
            recurrence='year'
        )

        stripe_subs_variant = stripe._get_product_price(subs_variant.id)
        self.assertEqual(stripe_subs_variant.unit_amount,  price)
