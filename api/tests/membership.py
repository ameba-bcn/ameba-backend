from django.utils import timezone
from rest_framework import status
from unittest import mock
from django.contrib.auth.models import Group

from api.tests.cart import BaseCartTest
from api.models import Subscription, Article, ItemVariant
from api import stripe

valid_payment_intent = {
    'status': stripe.IntentStatus.SUCCESS,
    'id': 'whatever',
    'amount': 1000
}


class TestSubscriptionPurchase(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'

    def test_cart_with_one_subscription_returns_200(self):
        user = self.get_user(1, member_profile=True)
        token = self.get_token(user).access_token
        cart = self.get_cart(
            user=user, item_variants=[1], item_class=Subscription,
            for_free=True
        )
        # Checkout cart
        checkout_details = dict(
            date_time=str(timezone.now()),
            payment_intent={'amount': cart.amount}
        )
        cart.set_checkout_details(checkout_details)
        cart.checkout()

        # Check has not active membership
        self.assertIn(user.member.status, [None, 'expired'])
        self.assertFalse(user.groups.filter(name='ameba_member'))
        # Purchase membership
        response = self.perform_payment(
            pk=cart.id, props=dict(payment_method_id='whatever'), token=token
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Check has membership
        self.assertIn(user.member.status, ['active'])
        # Check user included in group
        self.assertTrue(user.groups.filter(name='ameba_member'))

    def test_update_checked_out_cart_with_same_price_subscription_not_allowed(
        self
    ):
        user = self.get_user(1, member_profile=True)
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user)

        article = Article.objects.create(
            name='Article 1', description='None', is_active=True
        )
        article_variant = ItemVariant.objects.create(
            item=article, price=0, stock=10
        )
        cart.item_variants.set([article_variant.id])

        subscription = Subscription.objects.create(
            name='Subscription 1', description='None', is_active=True,
            group=Group.objects.get(name='ameba_member')
        )
        subscription_variant = ItemVariant.objects.create(
            item=subscription, price=0, stock=10
        )
        checkout_details = dict(
            date_time=str(timezone.now())
        )
        cart.set_checkout_details(checkout_details)
        cart.checkout()

        cart.item_variants.set([subscription_variant.id])

        response = self.perform_payment(
            pk=cart.id, props=dict(payment_method_id='whatever'), token=token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Checkout needed before continue.')
