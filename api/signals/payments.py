import django.dispatch
from django.dispatch import receiver

import api.stripe as stripe
from api.models import Payment
from api.exceptions import CheckoutNeeded, PaymentIsNotSucceed
from api.signals.items import items_acquired
from api.signals.emails import payment_successful

cart_processed = django.dispatch.Signal(
    providing_args=['cart', 'payment_method_id', 'request']
)


@receiver(cart_processed)
def on_cart_deleted(sender, cart, payment_method_id, request, **kwargs):
    # todo: use cart.checkout_details to store invoice in case there are
    #  unsuccessful payment attempt.
    if not cart.checkout_details:
        # If the cart has not checkout details, it can be normally deleted.
        return

    if cart.has_changed():
        # If the cart has changed, need to be checked-out before continue.
        raise CheckoutNeeded

    # Process payment
    payment_done = False
    if cart.amount > 0:
        # todo: control duplicated payment methods
        payment_method_id = stripe.create_payment_method(
            number='4242424242424242',
            exp_month=12,
            exp_year=2024,
            cvc=123
        )
        stripe.update_payment_method(cart.user, payment_method_id)

        if 'invoice' in cart.checkout_details:
            invoice_id = cart.checkout_details['invoice']['id']
            invoice = stripe.get_invoice(invoice_id)
        else:
            invoice = stripe.create_invoice(
                user=cart.user,
                cart_items=cart.get_cart_items()
            )
        invoice.pay(payment_method_id=payment_method_id)
        if invoice.status == 'paid':
            payment_done = True
    else:
        invoice = {}
        payment_done = True

    if not payment_done:
        cart.set_checkout_details({'invoice': dict(invoice)})
        raise PaymentIsNotSucceed

    # Add items to acquired lists
    items_acquired.send(sender=sender, cart=cart, request=request)

    # Create payment object
    payment = Payment.objects.create_payment(cart=cart, invoice=invoice)
    # Send payment confirmation email
    cart_record = payment.cart_record
    user = payment.user

    if payment.amount > 0:
        payment_successful.send(
            sender=sender, user=user, request=request, cart_record=cart_record
        )
