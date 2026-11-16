import time
import unittest.mock as mock

import rest_framework.status as status

import api.tests.helpers.carts as cart_helpers
import api.tests.helpers.user as user_helpers
import api.tests.helpers.items as item_helpers
import api.tests.helpers.subscriptions as subs_helpers
import api.tests.helpers.stripe as stripe_helper
import api.stripe as stripe
import api.tests._helpers as helpers
import api.mocks.stripe as stripe_mock
import api.models as api_models


class TestStripeWebhooks(helpers.BaseTest):
    DETAIL_ENDPOINT = '/api/stripe/'
    LIST_ENDPOINT = '/api/stripe/'

    def _check_user_acquired_paid_invoice_items(self, invoice, user):
        # Check invoice items are attached to user
        for invoice_item in invoice.lines['data']:
            item_variant = api_models.ItemVariant.objects.get(
                id=invoice_item['price']['product']
            )
            self.assertTrue(user.item_variants.filter(id=item_variant.id))

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    def test_succeeded_pre_existing_payment_closes_payment(self, send_to):
        user = user_helpers.get_user(
            username='Choco', email='choko@frito.com', password='12345'
        )
        cart = cart_helpers.get_cart(user=user, item_variants=[1, 2, 3])
        cart.checkout()
        payment = stripe.get_or_create_cart_payment(cart)

        # Check payment status
        self.assertEqual(payment.status, 'open')

        invoice = stripe.find_invoice(payment.invoice_id)
        invoice.status = 'paid'
        response = stripe_mock.mock_stripe_succeeded_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check cart is deleted
        self.assertFalse(api_models.Cart.objects.filter(id=cart.id))

        # Check payment status
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'paid')

        # Check invoice items
        self._check_user_acquired_paid_invoice_items(invoice, user)

        # Check email was sent
        send_to.assert_called_once()

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    @mock.patch('api.tasks.memberships.generate_email_with_qr_and_notify')
    def test_succeeded_subscription_renew_update_member_status(
        self, generate_email, payment_send
    ):
        member = user_helpers.get_member()
        membership = subs_helpers.subscribe_member(member=member, duration=0)
        s_variant = item_helpers.create_item_variant(
            membership.subscription, 10 * 100, -1, 'year'
        )

        # Check generated email with qr
        generate_email.assert_called_once()

        # Check member is inactive
        self.assertTrue(membership.is_expired)
        self.assertNotEqual(member.status, 'active')
        self.assertFalse(member.user.groups.filter(name='ameba_member'))

        # Create invoice and other stripe items
        customer = stripe_mock.Customer.create(
            id=str(member.user.id), name=member.user.username, email=member.user.email
        )
        price = stripe_mock.Price.create(
            currency='eur',
            product=str(s_variant.id),
            unit_amount=s_variant.price,
            recurring=dict(interval=s_variant.recurrence)
        )
        stripe_mock.InvoiceItem.create(
            customer=str(member.user.id), price=price['id']
        )
        invoice = stripe_mock.Invoice.create(
            id='invoice_id_subscription', customer=customer['id']
        )

        # Send webhook
        response = stripe_mock.mock_stripe_succeeded_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check payment have been created
        self.assertTrue(
            api_models.Payment.objects.filter(invoice_id=invoice['id'])
        )
        # Check member is active
        self.assertEqual(member.status, 'active')
        self.assertTrue(member.user.groups.filter(name='ameba_member'))

        # Check notifications
        payment_send.assert_called_once()
        generate_email.assert_called()

    @mock.patch('api.email_factories.RenewalFailedNotification.send_to')
    def test_failed_payment_creates_payment_but_has_no_effect(self, send_to):
        member = user_helpers.get_member()
        subscription = subs_helpers.create_subscription()
        s_variant = item_helpers.create_item_variant(
            subscription, 10 * 100, -1, 'year'
        )

        invoice = stripe_helper.get_invoice(
            user=member.user, item_variants=[s_variant], status='open'
        )

        # Send webhook
        response = stripe_mock.mock_stripe_failed_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check payment have been created
        self.assertTrue(
            api_models.Payment.objects.filter(invoice_id=invoice['id'])
        )
        # Check member has not created
        self.assertEqual(member.status, None)
        self.assertFalse(member.user.groups.filter(name='ameba_member'))

        # Check no email was sent
        send_to.assert_not_called()

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    @mock.patch('api.email_factories.RenewalFailedNotification.send_to')
    def test_failed_renew_keeps_subscription_for_stripe_retries(
        self, renewal_send, payment_send
    ):
        """ Smart Retries: a failed renewal attempt must not cancel the
        subscription (Stripe retries it and emails the customer). """
        member = user_helpers.get_member()
        membership = subs_helpers.subscribe_member(member=member, duration=0)
        s_variant = item_helpers.create_item_variant(
            membership.subscription, 10 * 100, -1, 'year'
        )

        # Check member is inactive
        self.assertTrue(membership.is_expired)
        self.assertNotEqual(member.status, 'active')
        self.assertFalse(member.user.groups.filter(name='ameba_member'))

        # Create invoice and other stripe items
        invoice = stripe_helper.get_invoice(
            user=member.user, item_variants=[s_variant], status='open'
        )
        # Invoice generated by Stripe for the yearly renewal
        invoice['billing_reason'] = 'subscription_cycle'

        # Send webhook
        response = stripe_mock.mock_stripe_failed_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check payment have been created
        self.assertTrue(
            api_models.Payment.objects.filter(invoice_id=invoice['id'])
        )
        # Check member is not active
        self.assertNotEqual(member.status, 'active')
        self.assertFalse(member.user.groups.filter(name='ameba_member'))

        # Subscription is left alone for Stripe to retry
        subscription_id = invoice['lines']['data'][0]['subscription']
        self.assertIn(subscription_id, stripe_mock.Subscription.objects)

        # No notifications from us (Stripe emails the customer)
        payment_send.assert_not_called()
        renewal_send.assert_not_called()

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    @mock.patch('api.tasks.memberships.generate_email_with_qr_and_notify')
    def test_upgrade_subscription_maintains_previous_one(
        self, generate_email, payment_send
    ):
        member = user_helpers.get_member()
        membership = subs_helpers.subscribe_member(member=member)
        old_group = membership.subscription.group.name
        s_variant = item_helpers.create_item_variant(
            membership.subscription, 10 * 100, -1, 'year'
        )

        # Check generated email with qr
        generate_email.assert_called_once()

        # Check member is active
        self.assertFalse(membership.is_expired)
        self.assertEqual(member.status, 'active')
        self.assertTrue(member.user.groups.filter(name=old_group))

        subs_pro = subs_helpers.create_subscription(name='ameba_pro')
        subs_pro_iv = item_helpers.create_item_variant(
            item=subs_pro,
            price=10,
            stock=-1,
            recurrence='year'
        )
        # Create cart
        cart = cart_helpers.get_cart(user=member.user)
        cart.item_variants.add(subs_pro_iv)
        cart.checkout()
        payment = stripe.get_or_create_cart_payment(cart)
        # Check payment status
        self.assertEqual(payment.status, 'open')

        # # Create invoice and other stripe items
        # invoice = stripe_helper.get_invoice(
        #     user=member.user, item_variants=[s_variant], status='paid'
        # )

        # Send webhook
        invoice = stripe.find_invoice(payment.invoice_id)
        invoice.status = 'paid'
        response = stripe_mock.mock_stripe_succeeded_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check payment have been created
        self.assertTrue(
            api_models.Payment.objects.filter(invoice_id=invoice['id'])
        )

        # Check member is active
        self.assertEqual(member.status, 'active')
        self.assertTrue(member.user.groups.filter(name=subs_pro.name))
        self.assertTrue(member.user.groups.filter(name=old_group))

        # Check notifications
        payment_send.assert_called_once()
        generate_email.assert_called()

        active_subs = stripe_mock.Subscription.list(
            customer=str(member.user.id)
        )
        self.assertEqual(len(active_subs['data']), 1)

    @mock.patch('api.email_factories.RenewalFailedNotification.send_to')
    def test_failed_new_membership_payment_does_not_cancel_subscription(
        self, renewal_send
    ):
        """ A member whose previous membership lapsed buys a new one and the
        first payment attempt fails (card declined, 3DS abandoned...). The new
        subscription must stay alive so the same PaymentIntent can be retried:
        before, it was treated as a failed renewal and canceled, which voided
        its invoice within minutes. """
        member = user_helpers.get_member()
        membership = subs_helpers.subscribe_member(member=member, duration=0)
        s_variant = item_helpers.create_item_variant(
            membership.subscription, 10 * 100, -1, 'year'
        )
        cart = cart_helpers.get_cart(user=member.user)
        cart.item_variants.add(s_variant)
        cart.checkout()
        payment = stripe.get_or_create_cart_payment(cart)
        invoice = stripe.find_invoice(payment.invoice_id)
        subscription_id = invoice.subscription
        self.assertEqual(invoice.billing_reason, 'subscription_create')

        response = stripe_mock.mock_stripe_failed_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(subscription_id, stripe_mock.Subscription.objects)
        self.assertEqual(stripe.find_invoice(payment.invoice_id).status,
                         'open')
        self.assertTrue(api_models.Cart.objects.filter(id=cart.id).exists())
        renewal_send.assert_not_called()

    def test_new_membership_cancels_past_due_subscriptions(self):
        member = user_helpers.get_member()
        subscription = subs_helpers.create_subscription()
        s_variant = item_helpers.create_item_variant(
            subscription, 10 * 100, -1, 'year'
        )
        price = stripe._get_product_price(str(s_variant.id))
        customer = str(member.user.id)
        old = stripe._create_subscription(customer, [{'price': price.id}])
        old.status = 'past_due'
        current = stripe._create_subscription(customer, [{'price': price.id}])
        current.status = 'active'

        stripe.cancel_previous_subscriptions(member.user, subscription)

        self.assertNotIn(old.id, stripe_mock.Subscription.objects)
        self.assertIn(current.id, stripe_mock.Subscription.objects)

    # -- Smart Retries: late renewal and final cancellation ------------------

    def _expired_member_with_renewal_invoice(self, period_start=None):
        member = user_helpers.get_member()
        membership = subs_helpers.subscribe_member(member=member, duration=0)
        s_variant = item_helpers.create_item_variant(
            membership.subscription, 10 * 100, -1, 'year'
        )
        invoice = stripe_helper.get_invoice(
            user=member.user, item_variants=[s_variant], status='open'
        )
        invoice['billing_reason'] = 'subscription_cycle'
        if period_start is not None:
            for line in invoice['lines']['data']:
                line['period']['start'] = period_start
        return member, membership, invoice

    def _subscription_deleted(self, invoice_id, subscription_id='sub_x'):
        return self.client.post(
            self.DETAIL_ENDPOINT, format='json',
            HTTP_STRIPE_SIGNATURE='sig',
            data={'type': 'customer.subscription.deleted', 'data': {
                'object': {'id': subscription_id, 'status': 'canceled',
                           'latest_invoice': invoice_id}
            }}
        )

    @mock.patch('api.email_factories.PaymentSuccessfulEmail.send_to')
    @mock.patch('api.tasks.memberships.generate_email_with_qr_and_notify')
    def test_renewal_paid_by_later_retry_renews_from_period_start(
        self, generate_email, payment_send
    ):
        period_start = int(time.time()) - 5 * 24 * 3600
        member, old_membership, invoice = \
            self._expired_member_with_renewal_invoice(period_start)

        # First attempt fails, a later retry succeeds
        stripe_mock.mock_stripe_failed_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )
        for _ in range(2):  # redelivered event is a no-op
            response = stripe_mock.mock_stripe_succeeded_payment(
                self.client, self.DETAIL_ENDPOINT, invoice
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        memberships = member.memberships.exclude(id=old_membership.id)
        self.assertEqual(memberships.count(), 1)
        renewed = memberships.get()
        # Covers the period Stripe charged for, not "from the retry date"
        self.assertEqual(int(renewed.starts.timestamp()), period_start)
        self.assertTrue(renewed.is_active)
        self.assertEqual(member.status, 'active')
        self.assertTrue(member.user.groups.filter(name='ameba_member'))
        self.assertEqual(
            api_models.Payment.objects.filter(invoice_id=invoice['id']).count(),
            1
        )
        payment_send.assert_called_once()

    @mock.patch('api.email_factories.RenewalFailedNotification.send_to')
    def test_subscription_canceled_after_retries_notifies_once(
        self, renewal_send
    ):
        member, _, invoice = self._expired_member_with_renewal_invoice()
        stripe_mock.mock_stripe_failed_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )
        renewal_send.assert_not_called()

        for _ in range(2):  # redelivered event
            response = self._subscription_deleted(invoice['id'])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        renewal_send.assert_called_once()
        self.assertEqual(renewal_send.call_args.kwargs['mail_to'],
                         member.user.email)

    @mock.patch('api.email_factories.RenewalFailedNotification.send_to')
    def test_subscription_canceled_member_already_renewed_no_notice(
        self, renewal_send
    ):
        """ e.g. the past_due subscription we cancel ourselves after the
        member bought a new membership """
        member, old_membership, invoice = \
            self._expired_member_with_renewal_invoice()
        stripe_mock.mock_stripe_failed_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )
        api_models.Membership.objects.create(  # active again
            member=member, duration=365,
            subscription=old_membership.subscription
        )

        self._subscription_deleted(invoice['id'])
        renewal_send.assert_not_called()

    @mock.patch('api.email_factories.RenewalFailedNotification.send_to')
    def test_abandoned_checkout_subscription_canceled_no_notice(
        self, renewal_send
    ):
        member = user_helpers.get_member()
        subscription = subs_helpers.create_subscription()
        s_variant = item_helpers.create_item_variant(
            subscription, 10 * 100, -1, 'year'
        )
        cart = cart_helpers.get_cart(user=member.user)
        cart.item_variants.add(s_variant)
        cart.checkout()
        payment = stripe.get_or_create_cart_payment(cart)

        response = self._subscription_deleted(payment.invoice_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        renewal_send.assert_not_called()
