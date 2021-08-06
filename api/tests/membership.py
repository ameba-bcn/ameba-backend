from django.utils import timezone
from rest_framework import status
from unittest import mock
from django.contrib.auth.models import Group

from api.tests.cart import BaseCartTest
from api.models import Subscription, Article, ItemVariant
from api import stripe

valid_payment_intent = {
    'status': stripe.IntentStatus.SUCCESS,
    'id': 'whatever'
}


class TestSubscriptionPurchase(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'

    @mock.patch('api.signals.payments.get_payment_intent', return_value={'status': stripe.IntentStatus.NOT_NEEDED})
    @mock.patch('api.signals.payments.get_create_update_payment_intent',
                return_value={'status': stripe.IntentStatus.NOT_NEEDED})
    def test_cart_with_one_subscription_returns_200(
        self, get_payment_intent, get_create_update_intent
    ):
        user = self.get_user(1, member_profile=True)
        token = self.get_token(user).access_token
        cart = self.get_cart(
            user=user, item_variants=[1], item_class=Subscription
        )
        # Checkout cart
        checkout_details = dict(
            date_time=str(timezone.now()),
            payment_intent={'amount': cart.amount}
        )
        checkout_details['payment_intent'].update(valid_payment_intent)
        cart.set_checkout_details(checkout_details)
        cart.checkout()

        # Check has not active membership
        self.assertIn(user.member.status, [None, 'expired'])
        self.assertFalse(user.groups.filter(name='ameba_member'))
        # Purchase membership
        response = self._delete(pk=cart.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Check has membership
        self.assertIn(user.member.status, ['active'])
        # Check user included in group
        self.assertTrue(user.groups.filter(name='ameba_member'))

    @mock.patch('api.signals.payments.get_create_update_payment_intent',
                return_value={'status': stripe.IntentStatus.NOT_NEEDED})
    def test_update_checked_out_cart_with_same_price_subscription_not_allowed(
        self, get_create_intent
    ):
        user = self.get_user(1, member_profile=True)
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user)

        article = Article.objects.create(
            name='Article 1', description='None', is_active=True
        )
        article_variant = ItemVariant.objects.create(
            item=article, price=10, stock=10
        )
        cart.item_variants.set([article_variant.id])

        subscription = Subscription.objects.create(
            name='Subscription 1', description='None', is_active=True,
            group=Group.objects.get(name='ameba_member')
        )
        subscription_variant = ItemVariant.objects.create(
            item=subscription, price=10, stock=10
        )
        checkout_details = dict(
            date_time=str(timezone.now()),
            payment_intent={'amount': cart.amount}
        )
        checkout_details['payment_intent'].update(valid_payment_intent)
        cart.set_checkout_details(checkout_details)
        cart.checkout()

        cart.item_variants.set([subscription_variant.id])

        response = self._delete(pk=cart.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Checkout needed before continue.')
