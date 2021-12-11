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
    # Get user
    user = cart.user

    # If the cart has changed, need to be checked-out before continue.
    if cart.has_changed():
        raise CheckoutNeeded

    # Process payment
    payment_done = False
    if cart.amount > 0:
        payment_method_id = stripe.get_payment_method_id(user, payment_method_id)
        invoice = stripe.get_or_create_invoice(cart)
        invoice.pay(payment_method=payment_method_id)
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
    if payment.amount > 0:
        cart_record = payment.cart_record
        payment_successful.send(
            sender=sender, user=user, request=request, cart_record=cart_record
        )
