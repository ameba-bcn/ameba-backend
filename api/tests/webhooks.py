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
        payment = stripe.create_payment_and_destroy_cart(cart)

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
            id=str(member.user.id), name=member.user.username
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
    def test_failed_renew_notifies_user_and_cancel_subscription(
        self, renewal_send, payment_send
    ):
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

        # Check notifications
        payment_send.assert_not_called()
        renewal_send.assert_called()

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
        payment = stripe.create_payment_and_destroy_cart(cart)
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
