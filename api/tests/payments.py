from unittest import mock
from rest_framework import status
from django.conf import settings
from django.contrib.auth.models import Group

from api import exceptions
import api.mocks.stripe as stripe_mock
import api.stripe as api_stripe
from api.models import Payment, Subscription, Member, Cart
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

    def test_get_payment_returns_api_public(self):
        item_variants = [1, 2, 3]
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=item_variants,
                             for_free=True)

        self.checkout(token=token)
        response = self.payment(pk=cart.id, token=token)

        self.assertIn('stripe_public', response.data)
        self.assertEqual(
            response.data['stripe_public'], settings.STRIPE_PUBLIC
        )

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


class CheckoutRobustnessTest(BaseCartTest):
    """ Payment endpoint reuses the open invoice of an unchanged cart, the
    cart lives until the payment succeeds, and fulfilment is idempotent. """
    WEBHOOK_ENDPOINT = '/api/stripe/'

    def setUp(self):
        stripe_mock.calls.clear()
        for store in (stripe_mock.Invoice, stripe_mock.InvoiceItem,
                      stripe_mock.Subscription, stripe_mock.PaymentIntent):
            store.objects.clear()
        self.user = self.get_user()
        self.token = self.get_token(self.user).access_token
        self.cart = self.get_cart(user=self.user, item_variants=[1, 2])

    def _checkout_and_pay(self):
        response = self.checkout(token=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.payment(token=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        return response

    def _calls(self, name):
        return [kw for call, kw in stripe_mock.calls if call == name]

    def _customer_invoices(self):
        return stripe_mock.Invoice.list(customer=str(self.user.id))['data']

    def test_unchanged_cart_returns_same_client_secret(self):
        first = self._checkout_and_pay()
        second = self.payment(token=self.token)
        self.checkout(token=self.token)
        third = self.payment(token=self.token)

        self.assertTrue(first.data['client_secret'])
        self.assertEqual(first.data['client_secret'],
                         second.data['client_secret'])
        self.assertEqual(first.data['client_secret'],
                         third.data['client_secret'])
        self.assertEqual(
            set(first.data.keys()),
            {'client_secret', 'payment_intent_id', 'stripe_public'}
        )
        # Only one invoice / payment for the customer
        self.assertEqual(len(self._customer_invoices()), 1)
        self.assertEqual(Payment.objects.filter(user=self.user).count(), 1)
        # The cart survives the payment creation
        self.assertTrue(Cart.objects.filter(id=self.cart.id).exists())

    def test_changed_cart_voids_previous_invoice(self):
        first = self._checkout_and_pay()
        old_payment = Payment.objects.get(user=self.user)
        old_invoice_id = old_payment.invoice_id

        self.cart.item_variants.remove(2)
        # A changed cart needs a checkout again
        self.assertEqual(self.payment(token=self.token).status_code,
                         status.HTTP_400_BAD_REQUEST)
        second = self._checkout_and_pay()

        self.assertNotEqual(first.data['client_secret'],
                            second.data['client_secret'])
        self.assertEqual(stripe_mock.Invoice.retrieve(old_invoice_id).status,
                         'void')
        old_payment.refresh_from_db()
        self.assertIsNone(old_payment.cart)
        self.assertEqual(old_payment.status, 'void')
        new_payment = Payment.objects.get(cart=self.cart)
        self.assertNotEqual(new_payment.id, old_payment.id)
        self.assertEqual(new_payment.amount, 1000)
        self.assertEqual(new_payment.status, 'open')

    def test_going_back_to_previous_contents_creates_fresh_invoice(self):
        first = self._checkout_and_pay()
        self.cart.item_variants.remove(2)
        self._checkout_and_pay()
        self.cart.item_variants.add(2)
        third = self._checkout_and_pay()
        # Same contents as the first attempt, but that invoice was voided:
        # the idempotency key must not replay it.
        self.assertNotEqual(first.data['client_secret'],
                            third.data['client_secret'])
        payment = Payment.objects.get(cart=self.cart)
        self.assertEqual(payment.status, 'open')
        self.assertEqual(payment.amount, 3000)

    def test_one_off_invoice_is_not_auto_advanced_nor_saves_card(self):
        self._checkout_and_pay()
        invoice_create = self._calls('Invoice.create')
        self.assertEqual(len(invoice_create), 1)
        self.assertIs(invoice_create[0]['auto_advance'], False)
        self.assertEqual(
            invoice_create[0]['pending_invoice_items_behavior'], 'exclude'
        )
        invoice_id = Payment.objects.get(user=self.user).invoice_id
        items = self._calls('InvoiceItem.create')
        self.assertEqual(len(items), 2)
        self.assertTrue(all(i['invoice'] == invoice_id for i in items))
        # Nothing left pending on the customer
        pending = [
            ii for ii in stripe_mock.InvoiceItem.objects.values()
            if ii.customer == str(self.user.id) and ii.invoice is None
        ]
        self.assertEqual(pending, [])
        # No setup_future_usage for tickets/shop
        self.assertEqual(self._calls('PaymentIntent.modify'), [])

    def test_membership_invoice_saves_card_for_renewals(self):
        user = self.get_user(user_tag=9, member_profile=True)
        token = self.get_token(user).access_token
        self.get_cart(user=user, item_variants=[5],
                      item_class=Subscription)
        self.checkout(token=token)
        response = self.payment(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        self.assertEqual(self._calls('Invoice.create')[0]['billing_reason'],
                         'subscription_create')
        modify = self._calls('PaymentIntent.modify')
        self.assertEqual(len(modify), 1)
        self.assertEqual(modify[0]['setup_future_usage'], 'off_session')
        # Same subscription reused on a second call
        again = self.payment(token=token)
        self.assertEqual(response.data['client_secret'],
                         again.data['client_secret'])
        self.assertEqual(len(self._calls('Subscription.create')), 1)

    def test_changed_membership_cart_cancels_incomplete_subscription(self):
        user = self.get_user(user_tag=9, member_profile=True)
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=[5],
                             item_class=Subscription)
        self.checkout(token=token)
        self.payment(token=token)
        old_invoice = Payment.objects.get(cart=cart).invoice_id
        subscription_id = stripe_mock.Invoice.retrieve(old_invoice).subscription
        self.assertIn(subscription_id, stripe_mock.Subscription.objects)

        self.create_items_variants([7])
        cart.item_variants.add(7)
        self.checkout(token=token)
        response = self.payment(token=token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._calls('Subscription.delete'),
                         [{'id': subscription_id}])
        self.assertEqual(stripe_mock.Invoice.retrieve(old_invoice).status,
                         'void')
        new_invoice = Payment.objects.get(cart=cart).invoice_id
        self.assertNotEqual(new_invoice, old_invoice)
        self.assertEqual(
            stripe_mock.Invoice.retrieve(new_invoice).status, 'open'
        )

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    def test_failed_payment_keeps_cart_and_same_client_secret(self, send_to):
        first = self._checkout_and_pay()
        invoice = stripe_mock.Invoice.retrieve(
            Payment.objects.get(user=self.user).invoice_id
        )
        response = stripe_mock.mock_stripe_failed_payment(
            self.client, self.WEBHOOK_ENDPOINT, invoice
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Cart.objects.filter(id=self.cart.id).exists())

        retry = self.payment(token=self.token)
        self.assertEqual(retry.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data['client_secret'],
                         retry.data['client_secret'])
        send_to.assert_not_called()

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    def test_cart_consumed_only_when_payment_succeeds(self, send_to):
        self._checkout_and_pay()
        payment = Payment.objects.get(user=self.user)
        self.assertTrue(Cart.objects.filter(id=self.cart.id).exists())
        self.assertFalse(self.user.item_variants.exists())

        invoice = stripe_mock.Invoice.retrieve(payment.invoice_id)
        response = stripe_mock.mock_stripe_succeeded_payment(
            self.client, self.WEBHOOK_ENDPOINT, invoice
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Cart.objects.filter(id=self.cart.id).exists())
        payment.refresh_from_db()
        self.assertTrue(payment.processed)
        self.assertEqual(
            set(self.user.item_variants.values_list('id', flat=True)), {1, 2}
        )
        send_to.assert_called_once()

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    def test_webhook_redelivery_fulfils_once(self, send_to):
        self._checkout_and_pay()
        payment = Payment.objects.get(user=self.user)
        invoice = stripe_mock.Invoice.retrieve(payment.invoice_id)
        for _ in range(3):
            response = stripe_mock.mock_stripe_succeeded_payment(
                self.client, self.WEBHOOK_ENDPOINT, invoice
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        send_to.assert_called_once()
        self.assertEqual(Payment.objects.filter(
            invoice_id=payment.invoice_id).count(), 1)

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    def test_paid_before_webhook_is_settled_on_cart_read(self, send_to):
        self._checkout_and_pay()
        payment = Payment.objects.get(user=self.user)
        stripe_mock.mark_invoice_paid(payment.invoice_id)

        response = self._get(pk='current', token=self.token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['id'], str(self.cart.id))
        self.assertEqual(response.data['item_variants'], [])
        self.assertFalse(Cart.objects.filter(id=self.cart.id).exists())
        payment.refresh_from_db()
        self.assertTrue(payment.processed)
        send_to.assert_called_once()

        # The webhook arriving afterwards is a no-op
        invoice = stripe_mock.Invoice.retrieve(payment.invoice_id)
        stripe_mock.mock_stripe_succeeded_payment(
            self.client, self.WEBHOOK_ENDPOINT, invoice
        )
        send_to.assert_called_once()

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    def test_paid_before_webhook_is_settled_on_payment_call(self, send_to):
        first = self._checkout_and_pay()
        payment = Payment.objects.get(user=self.user)
        stripe_mock.mark_invoice_paid(payment.invoice_id)

        again = self.payment(token=self.token)
        self.assertEqual(again.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data['client_secret'],
                         again.data['client_secret'])
        payment.refresh_from_db()
        self.assertTrue(payment.processed)
        self.assertFalse(Cart.objects.filter(id=self.cart.id).exists())
        send_to.assert_called_once()

    def test_deleting_cart_voids_its_pending_invoice(self):
        self._checkout_and_pay()
        payment = Payment.objects.get(user=self.user)
        Cart.objects.get(id=self.cart.id).delete()
        self.assertEqual(
            stripe_mock.Invoice.retrieve(payment.invoice_id).status, 'void'
        )
        payment.refresh_from_db()
        self.assertIsNone(payment.cart)

    def test_failed_invoice_creation_cleans_up_and_can_be_retried(self):
        self.checkout(token=self.token)
        real_create = stripe_mock.InvoiceItem.create.__func__
        state = {'count': 0}

        def flaky_create(cls, *args, **kwargs):
            state['count'] += 1
            if state['count'] == 2:
                raise RuntimeError('Stripe is down')
            return real_create(cls, *args, **kwargs)

        with mock.patch.object(stripe_mock.InvoiceItem, 'create',
                               classmethod(flaky_create)):
            with self.assertRaises(RuntimeError):
                api_stripe.get_or_create_cart_payment(self.cart)

        # Draft invoice and its first item were removed, no Payment saved
        self.assertEqual(self._customer_invoices(), [])
        self.assertEqual(
            [ii for ii in stripe_mock.InvoiceItem.objects.values()
             if ii.customer == str(self.user.id)], []
        )
        self.assertFalse(Payment.objects.filter(user=self.user).exists())
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.checkout_details['payment_attempts'], 1)

        # The retry works and gets a brand new invoice
        response = self.payment(token=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment = Payment.objects.get(user=self.user)
        self.assertEqual(payment.status, 'open')
        self.assertEqual(payment.amount, 3000)


class WebhookRequestValidationTest(BaseCartTest):
    WEBHOOK_ENDPOINT = '/api/stripe/'

    def test_missing_signature_header_is_400(self):
        response = self.client.post(
            self.WEBHOOK_ENDPOINT, data={'type': 'x'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_payload_is_400(self):
        response = self.client.post(
            self.WEBHOOK_ENDPOINT, data='not json', content_type='text/plain',
            HTTP_STRIPE_SIGNATURE='sig'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_signature_is_400(self):
        with mock.patch.object(
            stripe_mock.Webhook, 'construct_event',
            side_effect=stripe_mock.error.SignatureVerificationError('bad')
        ):
            response = self.client.post(
                self.WEBHOOK_ENDPOINT, data={'type': 'x'}, format='json',
                HTTP_STRIPE_SIGNATURE='sig'
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unhandled_event_is_200(self):
        response = self.client.post(
            self.WEBHOOK_ENDPOINT, data={'type': 'customer.created'},
            format='json', HTTP_STRIPE_SIGNATURE='sig'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mail_failure_does_not_fail_fulfilment(self):
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=[1, 2])
        self.checkout(token=token)
        self.payment(token=token)
        payment = Payment.objects.get(user=user)
        invoice = stripe_mock.Invoice.retrieve(payment.invoice_id)
        with mock.patch(
            'django.core.mail.EmailMultiAlternatives.send',
            side_effect=RuntimeError('Mailgun down')
        ), self.captureOnCommitCallbacks(execute=True):
            response = stripe_mock.mock_stripe_succeeded_payment(
                self.client, self.WEBHOOK_ENDPOINT, invoice
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertTrue(payment.processed)
        self.assertFalse(Cart.objects.filter(id=cart.id).exists())
