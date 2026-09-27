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
        invoice = stripe.create_invoice_from_cart(cart=cart)

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

    def test_stripe_invoice_includes_shipping_surcharge_when_shipping(self):
        user = user_helpers.get_user(
            username='mingonilo', email='mingonilo@mimail.si',
            password='ameba12345'
        )
        cart = cart_helpers.get_cart(
            user=user,
            item_variants=[1, 2, 3],
            item_class=api_models.Article
        )
        cart.delivery_method = 'shipping'
        cart.shipping_name = 'Someone'
        cart.shipping_address = 'Carrer Fake, 1'
        cart.shipping_postal_code = '08026'
        cart.shipping_city = 'Barcelona'
        cart.save()

        invoice = stripe.create_invoice_from_cart(cart=cart)

        # Amount charged matches cart.amount, which already includes the
        # shipping surcharge — total must never diverge from what's shown.
        self.assertEqual(cart.amount, invoice.amount_due)

        shipping_lines = [
            line for line in invoice.lines['data']
            if line['price']['product'] == stripe.SHIPPING_PRODUCT_ID
        ]
        self.assertEqual(len(shipping_lines), 1)
        self.assertEqual(
            shipping_lines[0]['price']['unit_amount'],
            stripe.SHIPPING_SURCHARGE_CENTS
        )

    def test_stripe_invoice_excludes_shipping_surcharge_when_pickup(self):
        user = user_helpers.get_user(
            username='mingonilo', email='mingonilo@mimail.si',
            password='ameba12345'
        )
        cart = cart_helpers.get_cart(
            user=user,
            item_variants=[1, 2, 3],
            item_class=api_models.Article
        )
        cart.delivery_method = 'pickup'
        cart.pickup_location = 'trama'
        cart.save()

        invoice = stripe.create_invoice_from_cart(cart=cart)

        self.assertEqual(cart.amount, invoice.amount_due)
        shipping_lines = [
            line for line in invoice.lines['data']
            if line['price']['product'] == stripe.SHIPPING_PRODUCT_ID
        ]
        self.assertEqual(len(shipping_lines), 0)

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
        invoice = stripe.create_invoice_from_cart(cart=cart)
        try:
            self.assertEqual(cart.amount, invoice.amount_due)
        except Exception as e:
            raise e
        finally:
            subs.delete()
            subs_variant.delete()
