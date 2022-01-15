import django.contrib.auth.models as auth_models

import rest_framework.status as status
import api.tests.helpers.carts as cart_helpers
import api.tests.helpers.user as user_helpers
import api.tests.helpers.items as item_helpers
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

    def test_succeeded_pre_existing_payment_closes_payment(self):
        user = user_helpers.get_user(
            username='Choco', email='choko@frito.com', password='12345'
        )
        cart = cart_helpers.get_cart(user=user, item_variants=[1, 2, 3])
        cart.checkout()
        payment = stripe.get_or_create_payment(cart)

        # Check payment status
        self.assertEqual(payment.status, 'open')

        invoice = payment.invoice
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

    def test_succeeded_subscription_renew_update_member_status(self):
        user = user_helpers.get_user(
            username='Member', email='member@frito.com', password='12345'
        )
        member = api_models.Member.objects.create(
            user=user,
            identity_card='55555555M',
            first_name='Member',
            last_name='Frito',
            phone_number='666666666'
        )
        subscription = item_helpers.create_item(
            pk=1, name='ameba_member', item_class=api_models.Subscription
        )
        s_variant = item_helpers.create_item_variant(
            subscription, 10 * 100, -1, 'year'
        )
        # Create expired membership
        membership = api_models.Membership.objects.create(
            member=member, duration=0, subscription=subscription
        )
        # Check member is inactive
        self.assertTrue(membership.is_expired)
        self.assertNotEqual(member.status, 'active')
        self.assertFalse(user.groups.filter(name='ameba_member'))

        # Create invoice and other stripe items
        customer = stripe_mock.Customer.create(
            id=str(user.id), name=user.username
        )
        price = stripe_mock.Price.create(
            currency='eur',
            product=str(s_variant.id),
            unit_amount=s_variant.price,
            recurring=dict(interval=s_variant.recurrence)
        )
        stripe_mock.InvoiceItem.create(
            customer=str(user.id), price=price['id']
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
        self.assertTrue(user.groups.filter(name='ameba_member'))
