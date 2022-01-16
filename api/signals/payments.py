from django.dispatch import receiver
import django.dispatch as dispatch

import api.stripe as api_stripe
import api.signals.emails as emails

invoice_payment = dispatch.Signal(providing_args=['invoice'])


@receiver(invoice_payment)
def process_invoice_payment(sender, invoice, **kwargs):
    payment = api_stripe.get_payment_from_invoice(invoice)

    if invoice['status'] == 'paid':
        payment.close()
        return

    if len(invoice['lines']['data']) != 1:
        return
    if invoice['lines']['data'][0]['type'] != 'subscription':
        return

    # Check whether payment is a renew by checking previous user's
    # subscriptions.
    item_variants = payment.item_variants.all()
    item_variant = item_variants.first()
    subscription = item_variant.item.subscription
    user = payment.user
    current_subs = [m.subscription for m in user.member.memberships.all()]
    if not subscription in current_subs:
        return

    canceled = api_stripe.cancel_subscription(invoice)
    if not canceled:
        return

    # Notify
    emails.failed_renewal.send(
        sender=sender,
        user=payment.user,
        subscription=item_variant.item.subscription
    )
