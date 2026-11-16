import logging

from django.db import transaction
from django.dispatch import receiver
import django.dispatch as dispatch

import api.stripe as api_stripe
import api.signals.emails as emails
import api.email_factories as email_factories

invoice_payment = dispatch.Signal(providing_args=['invoice'])

logger = logging.getLogger(__name__)

# Only invoices Stripe generates by itself for a yearly renewal. The first
# invoice of a new membership is 'subscription_create'; its failure just means
# the customer has to retry (same PaymentIntent) from the checkout page.
RENEWAL_BILLING_REASON = 'subscription_cycle'


@receiver(invoice_payment)
def process_invoice_payment(sender, invoice, **kwargs):
    if invoice['status'] == 'paid':
        api_stripe.fulfil_invoice_payment(invoice)
        return

    with transaction.atomic():
        payment = api_stripe.get_payment_from_invoice(invoice)
        _handle_failed_payment(sender, invoice, payment)


def _handle_failed_payment(sender, invoice, payment):
    """ A failed attempt never touches the cart nor the local payment: the
    customer can retry the same PaymentIntent. Only a failed membership
    *renewal* cancels the subscription and notifies the member.
    """
    log_ctx = {'invoice_id': invoice['id'], 'payment_id': str(payment.id),
               'billing_reason': invoice.get('billing_reason')}
    if invoice.get('billing_reason') != RENEWAL_BILLING_REASON:
        logger.info('Payment attempt failed, customer may retry %s', log_ctx)
        return

    if len(invoice['lines']['data']) != 1:
        return
    if invoice['lines']['data'][0]['type'] != 'subscription':
        return

    # Check whether payment is a renew by checking previous user's
    # subscriptions.
    item_variants = payment.item_variants.all()
    item_variant = item_variants.first()
    if item_variant is None or not item_variant.item.is_subscription():
        return
    subscription = item_variant.item.subscription
    user = payment.user
    if user is None or not user.has_member_profile():
        return
    current_subs = [m.subscription for m in user.member.memberships.all()]
    if subscription not in current_subs:
        return

    canceled = api_stripe.cancel_subscription(invoice)
    if not canceled:
        return
    logger.info('Renewal failed, subscription canceled %s', log_ctx)

    # Notify
    with email_factories.send_after_commit():
        emails.failed_renewal.send(
            sender=sender,
            user=payment.user,
            subscription=item_variant.item.subscription
        )
