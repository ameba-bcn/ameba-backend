import random
from django.conf import settings
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
            name='Socio',
            item_class=api_models.Subscription
        )
        price = random.randint(15, 20)
        subs_variant = item_helpers.create_item_variant(
            item=subs,
            price=price,
            stock=-1,
            recurrence='year'
        )

        stripe_subs_variant = stripe._get_product_price(str(subs_variant.id))

        try:
            self.assertEqual(stripe_subs_variant.unit_amount,  price * 100)
        except Exception as e:
            raise e
        finally:
            subs.delete()
            subs_variant.delete()

    def test_new_item_variant_updates_stripe_product_price(self):
        subs = item_helpers.create_item(
            name='Socio',
            item_class=api_models.Subscription
        )
        price = 15
        subs_variant = item_helpers.create_item_variant(
            item=subs,
            price=price,
            stock=-1,
            recurrence='year'
        )

        stripe_subs_variant = stripe._get_product_price(str(subs_variant.id))

        try:
            self.assertEqual(stripe_subs_variant.unit_amount,  price * 100)
        except Exception as e:
            subs.delete()
            subs_variant.delete()
            raise e

        price = 20
        subs_variant.price = price
        subs_variant.save()

        stripe_subs_variant = stripe._get_product_price(str(subs_variant.id))
        try:
            self.assertEqual(stripe_subs_variant.unit_amount,  price * 100)
        except Exception as e:
            raise e
        finally:
            subs.delete()
            subs_variant.delete()

    def test_stripe_subscription_invoice_generation_from_cart(self):
        user = user_helpers.get_user(
            username='mingonilo',
            email='mingonilo@mimail.si',
            password='ameba12345'
        )
        cart = cart_helpers.get_cart(
            user=user,
            item_variants=[1, ],
            item_class=api_models.Subscription
        )
        invoice = stripe.create_invoice(
            user=user,
            cart_items=cart.get_cart_items()
        )

        self.assertEqual(cart.amount, invoice.amount_due)

    def test_stripe_articles_invoice_generation_from_cart(self):
        user = user_helpers.get_user(
            username='mingonilo',
            email='mingonilo@mimail.si',
            password='ameba12345'
        )
        cart = cart_helpers.get_cart(
            user=user,
            item_variants=[1, 2, 3],
            item_class=api_models.Article
        )
        invoice = stripe.create_invoice_from_cart(cart=cart)
        self.assertEqual(cart.amount, invoice.amount_due)

    def test_stripe_subscription_and_articles_invoice_generation_from_cart(self):
        user = user_helpers.get_user(
            username='mingonilo',
            email='mingonilo@mimail.si',
            password='ameba12345'
        )
        cart = cart_helpers.get_cart(
            user=user,
            item_variants=[1, 2, 3],
            item_class=api_models.Article
        )

        subs = item_helpers.create_item(
            name='Socio',
            item_class=api_models.Subscription
        )
        price = random.randint(15, 20)
        subs_variant = item_helpers.create_item_variant(
            pk=4,
            item=subs,
            price=price,
            stock=-1,
            recurrence='year'
        )
        cart.item_variants.add(subs_variant)
        invoice = stripe.create_invoice(
            user=user,
            cart_items=cart.get_cart_items()
        )
        try:
            self.assertEqual(cart.amount, invoice.amount_due)
        except Exception as e:
            raise e
        finally:
            subs.delete()
            subs_variant.delete()
