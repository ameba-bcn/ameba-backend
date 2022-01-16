from django.utils import timezone
from rest_framework import status
from django.contrib.auth.models import Group

from api.tests.cart import BaseCartTest
from api.models import Subscription, Article, ItemVariant
import api.stripe as api_stripe
import api.tests.helpers.user as user_helpers
import api.tests.helpers.subscriptions as subs_helpers
import api.tests.helpers.carts as cart_helpers
import api.tests.helpers.items as item_helpers

valid_payment_intent = {
    'status': api_stripe.IntentStatus.SUCCESS,
    'id': 'whatever',
    'amount': 1000
}


class TestSubscriptionPurchase(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'

    def test_cart_with_one_free_subscription_returns_200(self):
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
        response = self.payment(pk=cart.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

        response = self.payment(
            pk=cart.id, token=token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Checkout needed before continue.')

    def test_checkout_with_already_active_subscription_is_not_allowed(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        membership = subs_helpers.subscribe_member(member=member)
        sub_iv = item_helpers.create_item_variant(item=membership.subscription)

        cart = cart_helpers.get_cart(user=member.user)
        cart.item_variants.add(sub_iv)

        response = self.checkout('current', token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Cart has already active subscription.')
