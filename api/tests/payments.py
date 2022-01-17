from unittest import mock
from rest_framework import status
from django.conf import settings
from django.contrib.auth.models import Group

from api import exceptions
from api.models import Payment, Subscription, Member
from api.tests.cart import BaseCartTest


class PaymentFlowTest(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'
    LIST_ENDPOINT = '/api/carts/'

    def setUp(self):
        self.debug = settings.DEBUG
        settings.DEBUG = False

    def tearDown(self):
        settings.DEBUG = self.debug

    def check_cart_summary(self, item_variants, cart_summary):
        found_items = []
        for summary_item in cart_summary['item_variants']:
            if summary_item['id'] in item_variants:
                item_variant = summary_item['id']
                found_items.append(item_variant)
                self.assertIn('price', summary_item)
                self.assertIn('subtotal', summary_item)
                self.assertIn('discount_value', summary_item)
                self.assertIn('discount_name', summary_item)
        self.assertEqual(item_variants.sort(), found_items.sort())

    def test_cart_checkout_returns_cart_summary(self):
        item_variants = [1, 2]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=item_variants)

        response = self.checkout(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], 3000)
        self.assertEqual(response.data['total'], '30.00 €')
        self.check_cart_summary(item_variants=item_variants, cart_summary=response.data)

    def test_cart_checkout_starts_payment_process(self):
        item_variants = [1, 2]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=item_variants)

        response = self.checkout(token=token)
        self.assertIn('checkout', response.data)

    def test_empty_cart_checkout_is_not_possible(self):
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user)
        response = self.checkout(token=token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'], exceptions.CartIsEmpty.default_detail
        )

    def test_others_cart_checkout_is_forbidden(self):
        user_1 = self.get_user(1)
        token_1 = self.get_token(user_1).access_token

        user_2 = self.get_user(2)
        cart_2 = self.get_cart(user=user_2)
        response = self.checkout(pk=cart_2.id, token=token_1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cart_checkout_after_cart_update_has_same_stripe_data(self):
        item_variants = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=item_variants)

        response_1 = self.checkout(token=token)
        cart.item_variants.remove(3)
        response_2 = self.checkout(token=token)

        self.assertEqual(
            response_1.data['checkout'], response_2.data['checkout']
        )

    def test_cart_second_checkout_update_prices_if_items_changed(self):
        item_variants = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=item_variants)
        self.assertIsNone(cart.checkout_details)

        response_1 = self.checkout(token=token)
        cart.refresh_from_db()

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_1.data['amount'], 6000)

        cart.item_variants.remove(3)
        response_2 = self.checkout(token=token)
        cart.refresh_from_db()

        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_2.data['amount'], 3000)

    @mock.patch('django.conf.settings.DEBUG', True)
    def test_stored_payment_has_relevant_cart_data(self):
        item_variants = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=item_variants,
                             for_free=True)

        self.checkout(token=token)
        response = self.payment(pk=cart.id, token=token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Payment.objects.filter(id=cart.id))
        payment = Payment.objects.get(id=cart.id)
        self.check_cart_summary(item_variants=item_variants, cart_summary=payment.cart_record)
        self.assertEqual(payment.amount, 0)

    @mock.patch('django.conf.settings.DEBUG', True)
    def test_stored_payment_has_relevant_payment_data(self):
        pass
        # todo: rework this test with new flow
        # item_variants = [1, 2, 3]
        # user = self.get_user()
        # token = self.get_token(user).access_token
        # cart = self.get_cart(user=user, item_variants=item_variants)
        #
        # checkout_response = self.checkout(token=token)
        # payment_intent_secret = checkout_response.data['checkout']['client_secret']
        #
        # self._delete(pk='current', token=token)
        # payment = Payment.objects.get(id=cart.id)
        # self.assertEqual(
        #     payment_intent_secret, payment.details['client_secret']
        # )

    def test_pay_not_checkout_out_cart_is_not_possible(self):
        item_variants = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        self.get_cart(user=user, item_variants=item_variants)
        response = self.payment(pk='current', token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_cart_no_auth_is_not_possible(self):
        item_variants = [1, 2, 3]
        user = self.get_user()
        cart = self.get_cart(user=user, item_variants=item_variants)

        response = self._delete(pk=cart.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_cart_price_0_is_possible(self):
        item_variants = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=item_variants,
                             for_free=True)

        checkout_response = self.checkout(token=token)
        self.assertEqual(checkout_response.data['checkout'], {})
        response = self.payment(pk=cart.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment = Payment.objects.get(id=cart.id)
        self.assertEqual(payment.status, 'paid')

    def test_update_from_price_to_free(self):
        pass
        # todo: rework with new flow
        # item_variants = [1, 2, 3]
        # user = self.get_user()
        # token = self.get_token(user).access_token
        # cart = self.get_cart(user=user, item_variants=item_variants)
        # checkout_response = self.checkout(token=token)
        # self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)
        # self.assertTrue(checkout_response.data['checkout'])
        # new_variants = [4, 5]
        # self.create_items_variants(item_variants=new_variants, for_free=True)
        # cart.item_variants.set(new_variants)
        # checkout_response = self.checkout(token=token)
        # self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)
        # self.assertFalse(checkout_response.data['checkout'])

    def test_update_from_free_to_price(self):
        pass
        # todo: rework test with new flow
        # item_variants = [1, 2, 3]
        # user = self.get_user()
        # token = self.get_token(user).access_token
        # cart = self.get_cart(
        #     user=user, item_variants=item_variants, for_free=True
        # )
        # checkout_response = self.checkout(token=token)
        # self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)
        # self.assertFalse(checkout_response.data['checkout'])
        # new_variants = [4, 5]
        # self.create_items_variants(item_variants=new_variants)
        # cart.item_variants.set(new_variants)
        # checkout_response = self.checkout(token=token)
        # self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)
        # self.assertEqual(cart.amount, checkout_response.data['amount'])
        # self.assertTrue(checkout_response.data['checkout']['client_secret'])
