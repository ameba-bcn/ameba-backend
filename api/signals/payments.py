import logging

from django.db import transaction
from django.dispatch import receiver
import django.dispatch as dispatch

import api.stripe as api_stripe
import api.signals.emails as emails
import api.email_factories as email_factories

invoice_payment = dispatch.Signal(providing_args=['invoice'])
subscription_deleted = dispatch.Signal(providing_args=['subscription'])

logger = logging.getLogger(__name__)

# Only invoices Stripe generates by itself for a yearly renewal. The first
# invoice of a new membership is 'subscription_create'; its failure just means
# the customer has to retry (same PaymentIntent) from the checkout page.
RENEWAL_BILLING_REASON = 'subscription_cycle'
# Invoice statuses of a renewal Stripe gave up on (Smart Retries exhausted)
UNPAID_INVOICE_STATUSES = ('open', 'uncollectible')
RENEWAL_FAILED_NOTIFIED = 'renewal_failed_notified'


@receiver(invoice_payment)
def process_invoice_payment(sender, invoice, **kwargs):
    if invoice['status'] == 'paid':
        # Also covers a renewal paid by a later Smart Retry: the payment
        # created on the first failure is found by invoice id and fulfilled
        # once (it renews the membership).
        api_stripe.fulfil_invoice_payment(invoice)
        return

    with transaction.atomic():
        payment = api_stripe.get_payment_from_invoice(invoice)
        _log_failed_payment(invoice, payment)


def _log_failed_payment(invoice, payment):
    """ A failed attempt never changes anything: not the cart, not the local
    payment and not the Stripe subscription.

    - New purchase: the customer retries the same PaymentIntent.
    - Membership renewal: Stripe Smart Retries charge it again over the next
      days and email the customer each time (Dashboard settings). The
      subscription is canceled by Stripe once all retries fail (see
      process_subscription_deleted). Nothing to do here, so we no longer
      cancel the subscription on the first failure nor send our own email
      (it duplicated Stripe's and pointed to buying a new membership while
      Stripe was still retrying the current one).
    """
    logger.info(
        'Payment attempt failed %s',
        {'invoice_id': invoice['id'], 'payment_id': str(payment.id),
         'billing_reason': invoice.get('billing_reason'),
         'attempt_count': invoice.get('attempt_count'),
         'next_payment_attempt': invoice.get('next_payment_attempt')}
    )


@receiver(subscription_deleted)
def process_subscription_deleted(sender, subscription, **kwargs):
    """ customer.subscription.deleted: Stripe canceled a membership
    subscription. Membership access needs nothing here (it ends with the
    membership's own expiry date). We only tell the member once that the
    renewal could not be charged, when:
    - the subscription's last invoice is an unpaid renewal (Stripe gave up
      after the retries), and
    - the member has no active membership (e.g. not an old subscription we
      canceled ourselves because they bought a new membership).
    """
    invoice_id = subscription.get('latest_invoice')
    if not invoice_id:
        return
    invoice = api_stripe.find_invoice(invoice_id)
    if invoice is None or invoice['billing_reason'] != RENEWAL_BILLING_REASON \
            or invoice['status'] not in UNPAID_INVOICE_STATUSES:
        return

    with transaction.atomic():
        payment = api_stripe.get_payment_from_invoice(invoice)
        details = dict(payment.details or {})
        if details.get(RENEWAL_FAILED_NOTIFIED):
            return
        user = payment.user
        if user is None or not user.has_member_profile() \
                or user.member.is_active:
            return
        item_variant = payment.item_variants.filter(
            item__subscription__isnull=False
        ).first()
        if item_variant is None:
            return

        details[RENEWAL_FAILED_NOTIFIED] = True
        payment.details = details
        payment.save(update_fields=['details'])
        logger.info('Renewal not charged after retries, subscription %s '
                    'canceled, notifying user %s (invoice %s)',
                    subscription.get('id'), user.id, invoice_id)
        with email_factories.send_after_commit():
            emails.failed_renewal.send(
                sender=sender,
                user=user,
                subscription=item_variant.item.subscription
            )
