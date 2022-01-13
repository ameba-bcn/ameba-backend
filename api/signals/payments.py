from django.dispatch import receiver
import django.dispatch as dispatch

import api.stripe as api_stripe

invoice_payment_succeeded = dispatch.Signal(providing_args=['invoice'])
invoice_payment_failed = dispatch.Signal(providing_args=['invoice'])


@receiver(invoice_payment_succeeded)
def process_succeeded_invoice_payment(sender, invoice, **kwargs):
    payment = api_stripe.get_payment_from_invoice(invoice)
    payment.close()


@receiver(invoice_payment_failed)
def process_failed_invoice_payment(sender, invoice, **kwargs):
    pass
