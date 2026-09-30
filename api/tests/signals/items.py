import itertools
import unittest.mock as mock

import api.mocks.stripe as stripe_mock
import api.models as api_models
import api.stripe as stripe
import api.tests._helpers as helpers
import api.tests.helpers.carts as cart_helpers
import api.tests.helpers.user as user_helpers

_user_counter = itertools.count()


class ArticleDeliveryEmailContextTest(helpers.BaseTest):
    """ Article purchases carry a delivery method (pickup/shipping) which
    must be propagated: from Cart -> Order (via Payment.cart_record, since
    the Cart row is deleted before Orders are created) -> the transactional
    emails sent to the buyer and to Ameba staff. """

    WEBHOOK_ENDPOINT = '/api/stripe/'

    def _get_paid_article_cart(self, delivery_method='pickup', **shipping):
        suffix = next(_user_counter)
        user = user_helpers.get_user(
            username=f'delivery_user_{suffix}',
            email=f'delivery_user_{suffix}@ameba.cat',
            password='ameba12345'
        )
        cart = cart_helpers.get_cart(
            user=user, item_variants=[1], item_class=api_models.Article
        )
        cart.delivery_method = delivery_method
        for key, value in shipping.items():
            setattr(cart, key, value)
        cart.save()
        cart.checkout()
        return cart, user

    def _pay(self, cart):
        """ Runs a cart through the full (mocked) Stripe flow so that
        Payment.close() actually runs and item_acquired fires — payment
        stays 'open' until the invoice.payment_succeeded webhook lands,
        same as in api/tests/webhooks.py. """
        payment = stripe.create_payment_and_destroy_cart(cart)
        invoice = stripe.find_invoice(payment.invoice_id)
        invoice.status = 'paid'
        response = stripe_mock.mock_stripe_succeeded_payment(
            self.client, self.WEBHOOK_ENDPOINT, invoice
        )
        assert response.status_code == 200
        return payment

    @mock.patch('api.email_factories.NewOrderInternalNotification.send_to')
    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    def test_pickup_order_created_with_pickup_location(
        self, payment_send_to, new_order_send_to
    ):
        cart, user = self._get_paid_article_cart(
            delivery_method='pickup', pickup_location='trama'
        )
        self._pay(cart)

        order = api_models.Order.objects.get(user=user)
        self.assertEqual(order.delivery_method, 'pickup')
        self.assertEqual(order.pickup_location, 'trama')
        self.assertEqual(order.shipping_address, '')

        new_order_send_to.assert_called_once()
        self.assertEqual(
            new_order_send_to.call_args.kwargs['delivery_method'], 'pickup'
        )
        self.assertIn(
            'Trama Serigrafia',
            new_order_send_to.call_args.kwargs['pickup_location']
        )

        payment_send_to.assert_called_once()
        self.assertEqual(
            payment_send_to.call_args.kwargs['delivery_method'], 'pickup'
        )
        self.assertTrue(payment_send_to.call_args.kwargs['has_articles'])

    @mock.patch('api.email_factories.NewOrderInternalNotification.send_to')
    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    def test_shipping_order_created_with_shipping_address(
        self, payment_send_to, new_order_send_to
    ):
        cart, user = self._get_paid_article_cart(
            delivery_method='shipping',
            shipping_name='Jane Doe',
            shipping_address='Carrer Fake, 1',
            shipping_postal_code='08026',
            shipping_city='Barcelona'
        )
        self._pay(cart)

        order = api_models.Order.objects.get(user=user)
        self.assertEqual(order.delivery_method, 'shipping')
        self.assertEqual(order.shipping_name, 'Jane Doe')
        self.assertEqual(order.shipping_address, 'Carrer Fake, 1')
        self.assertEqual(order.shipping_postal_code, '08026')
        self.assertEqual(order.shipping_city, 'Barcelona')

        new_order_send_to.assert_called_once()
        self.assertEqual(
            new_order_send_to.call_args.kwargs['delivery_method'], 'shipping'
        )
        self.assertIn(
            'Carrer Fake, 1',
            new_order_send_to.call_args.kwargs['shipping_address']
        )

        payment_send_to.assert_called_once()
        self.assertEqual(
            payment_send_to.call_args.kwargs['delivery_method'], 'shipping'
        )
        self.assertIn(
            'Carrer Fake, 1',
            payment_send_to.call_args.kwargs['shipping_address']
        )

    @mock.patch('api.email_factories.OrderReadyNotification.send_to')
    def test_order_ready_notification_uses_pickup_context(self, send_to):
        cart, user = self._get_paid_article_cart(
            delivery_method='pickup', pickup_location='merla'
        )
        self._pay(cart)
        order = api_models.Order.objects.get(user=user)

        order.ready = True
        order.save()

        # Sent once to the user and once internally.
        self.assertEqual(send_to.call_count, 2)
        for call in send_to.call_args_list:
            self.assertEqual(call.kwargs['delivery_method'], 'pickup')
            self.assertIn('La Merla', call.kwargs['pickup_location'])

    @mock.patch('api.email_factories.OrderReadyNotification.send_to')
    def test_order_ready_notification_uses_shipping_context(self, send_to):
        cart, user = self._get_paid_article_cart(
            delivery_method='shipping',
            shipping_name='Jane Doe',
            shipping_address='Carrer Fake, 1',
            shipping_postal_code='08026',
            shipping_city='Barcelona'
        )
        self._pay(cart)
        order = api_models.Order.objects.get(user=user)

        order.ready = True
        order.save()

        self.assertEqual(send_to.call_count, 2)
        for call in send_to.call_args_list:
            self.assertEqual(call.kwargs['delivery_method'], 'shipping')
            self.assertIn('Carrer Fake, 1', call.kwargs['shipping_address'])
