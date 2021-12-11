import unittest.mock as mock

import django.conf as conf
import rest_framework.status as status

import api.tests.helpers.items as item_helpers
import api.tests.helpers.carts as cart_helpers
import api.email_factories as email_factories
import api.tests.helpers.user as user_helpers
import api.tests._helpers as test_helpers
import api.models as api_models
import api.stripe as stripe


class TestPaymentsFlow(test_helpers.BaseTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'
    PAYMENT = '/api/carts/{pk}/perform_payment/'
    CHECKOUT = '/api/carts/{pk}/checkout/'

    def setUp(self):
        self.stripe_sync = conf.settings.STRIPE_SYNC
        conf.settings.STRIPE_SYNC = True

    def tearDown(self):
        conf.settings.STRIPE_SYNC = self.stripe_sync

    @mock.patch.object(email_factories.PaymentSuccessfulEmail, 'send_to')
    def test_single_article_purchase_flow(self, send_to):
        # Create user
        user_attrs = dict(
            email='one@user.com',
            username='one_user',
            password='ameba12345',

        )
        user = user_helpers.get_user(**user_attrs)
        token = user_helpers.get_user_token(user)

        # Create cart with article
        item_variants = [1, 2, 3]
        cart = cart_helpers.get_cart(
            user=user,
            item_variants=item_variants,
            item_class=api_models.Article
        )

        # Check cart exists
        cart_url = self.DETAIL_ENDPOINT.format(pk=cart.pk)
        response = self.request(url=cart_url, method='get', token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checkout cart
        checkout_url = self.CHECKOUT.format(pk=cart.pk)
        response = self.request(url=checkout_url, method='get', token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create payment method for user
        payment_method_attrs = dict(
            number='4242424242424242',
            exp_year='2035',
            exp_month='12',
            cvc='333'
        )
        pm_id = stripe.create_payment_method(**payment_method_attrs)
        actual_pm_id = stripe.get_payment_method_id(user, pm_id)
        # Process payment
        url = self.PAYMENT.format(pk=cart.pk)
        props = {'payment_method_id': actual_pm_id}
        response = self.request(url=url, method='post', token=token,
                                props=props)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check cart does not exist
        cart_url = self.DETAIL_ENDPOINT.format(pk=cart.pk)
        response = self.request(url=cart_url, method='get', token=token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Check user received article
        for var_id in item_variants:
            item_variant = api_models.ItemVariant.objects.get(id=var_id)
            acquired = item_variant.acquired_by.filter(id=user.id).exists()
            self.assertTrue(acquired)

        # Check payment has been stored and is paid
        payment = api_models.Payment.objects.last()
        self.assertEqual(payment.status, 'paid')

        # Check email has been sent to user
        send_to.assert_called()
