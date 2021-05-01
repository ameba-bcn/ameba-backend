from rest_framework import status

from api import exceptions
from api.models import Payment
from api.tests.cart import BaseCartTest


class PaymentFlowTest(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'
    LIST_ENDPOINT = '/api/carts/'
    CHECKOUT_ENDPOINT = '/api/carts/{pk}/checkout/'

    def checkout(self, pk='current', token=None):
        self._authenticate(token=token)
        return self.client.get(self.CHECKOUT_ENDPOINT.format(pk=pk))

    def check_cart_summary(self, items, cart_summary):
        found_items = []
        for summary_item in cart_summary['cart_items']:
            for item in items:
                if summary_item['name'] == f'item_{item}':
                    found_items.append(items)
                    self.assertEqual(summary_item['price'], f'{item * 10}.00€')
                    self.assertEqual(summary_item['subtotal'], f'{item * 10}.00€')
                    self.assertEqual(summary_item['discount_value'], '')
                    self.assertEqual(summary_item['discount_name'], '')
        self.assertEqual(items.sort(), found_items.sort())

    def test_cart_checkout_returns_cart_summary(self):
        items = [1, 2]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, items=items)

        response = self.checkout(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], 3000)
        self.assertEqual(response.data['total'], '30.00 €')
        self.check_cart_summary(items=items, cart_summary=response.data)

    def test_cart_checkout_starts_payment_process(self):
        items = [1, 2]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, items=items)

        response = self.checkout(token=token)
        self.assertIn('checkout', response.data)
        self.assertIn('client_secret', response.data['checkout'])
        self.assertTrue(response.data['checkout']['client_secret'])

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
        items = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, items=items)

        response_1 = self.checkout(token=token)
        cart.item_variants.remove(3)
        response_2 = self.checkout(token=token)

        self.assertEqual(
            response_1.data['checkout'], response_2.data['checkout']
        )

    def test_cart_second_checkout_update_prices_if_items_changed(self):
        items = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, items=items)
        self.assertIsNone(cart.checkout_details)

        response_1 = self.checkout(token=token)
        cart.refresh_from_db()
        checkout_details_1 = cart.checkout_details

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_1.data['amount'], 6000)
        self.assertEqual(checkout_details_1['payment_intent']['amount'], 6000)

        cart.item_variants.remove(3)
        response_2 = self.checkout(token=token)
        cart.refresh_from_db()
        checkout_details_2 = cart.checkout_details

        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_2.data['amount'], 3000)
        self.assertEqual(checkout_details_2['payment_intent']['amount'], 3000)

    def test_delete_checked_out_cart_saves_payment(self):
        items = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, items=items)

        self.checkout(token=token)
        delete_response = self._delete(pk='current', token=token)

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Payment.objects.filter(id=cart.id))

    def test_stored_payment_has_relevant_cart_data(self):
        items = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, items=items)

        self.checkout(token=token)
        delete_response = self._delete(pk='current', token=token)

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Payment.objects.filter(id=cart.id))
        payment = Payment.objects.get(id=cart.id)
        self.check_cart_summary(items=items, cart_summary=payment.cart_record)
        self.assertEqual(payment.amount, 6000)

    def test_stored_payment_has_relevant_payment_data(self):
        items = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, items=items)

        checkout_response = self.checkout(token=token)
        payment_intent_secret = checkout_response.data['checkout']['client_secret']

        self._delete(pk='current', token=token)
        payment = Payment.objects.get(id=cart.id)
        self.assertEqual(
            payment_intent_secret, payment.details['client_secret']
        )

    def test_delete_not_checkout_out_cart_is_not_possible(self):
        items = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, items=items)

        response = self._delete(pk='current', token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'],
            exceptions.CartCheckoutNotProcessed.default_detail
        )

    def test_delete_cart_no_auth_is_not_possible(self):
        items = [1, 2, 3]
        user = self.get_user()
        cart = self.get_cart(user=user, items=items)

        response = self._delete(pk=cart.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
