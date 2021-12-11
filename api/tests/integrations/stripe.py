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
    def setUp(self):
        self.stripe_sync = settings.STRIPE_SYNC
        settings.STRIPE_SYNC = True

    def tearDown(self):
        settings.STRIPE_SYNC = self.stripe_sync

    def test_new_item_variant_creates_stripe_product(self):
        subs = item_helpers.create_item(
            pk=1,
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

        stripe_subs_variant = stripe._get_product_price(subs_variant.id)
        self.assertEqual(stripe_subs_variant.unit_amount,  price * 100)

        subs_variant.delete()
        subs.delete()

    def test_new_item_variant_updates_stripe_product_price(self):
        subs = item_helpers.create_item(
            pk=1,
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

        stripe_subs_variant = stripe._get_product_price(subs_variant.id)
        self.assertEqual(stripe_subs_variant.unit_amount,  price * 100)

        price = 20
        subs_variant.price = price
        subs_variant.save()

        stripe_subs_variant = stripe._get_product_price(subs_variant.id)
        self.assertEqual(stripe_subs_variant.unit_amount,  price * 100)

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
        invoice = stripe.create_invoice(
            user=user,
            cart_items=cart.get_cart_items()
        )
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
            pk=4,
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
        self.assertEqual(cart.amount, invoice.amount_due)

    def test_stripe_complete_flow(self):
        user = user_helpers.get_user(
            username='mungonuli',
            email='mungonuli@mimail.si',
            password='ameba12345'
        )
        cart = cart_helpers.get_cart(
            user=user,
            item_variants=[1, 2, 3],
            item_class=api_models.Article
        )

        subs = item_helpers.create_item(
            pk=4,
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

        payment_method_id = stripe.create_payment_method(
            number='4242424242424242',
            exp_month=12,
            exp_year=2024,
            cvc=123
        )
        stripe.update_payment_method(user, payment_method_id)
        invoice = stripe.create_invoice(
            user=user,
            cart_items=cart.get_cart_items()
        )
        invoice.pay(payment_method_id=payment_method_id)
        self.assertEqual(invoice.status, 'paid')
