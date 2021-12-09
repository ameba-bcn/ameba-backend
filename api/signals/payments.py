import django.dispatch
from django.dispatch import receiver

from api.stripe import get_payment_intent
from api.models import Payment
from api.exceptions import CheckoutNeeded, PaymentIsNotSucceed
from api.signals.items import items_acquired
from api.signals.emails import payment_successful

cart_processed = django.dispatch.Signal(
    providing_args=['cart', 'payment_method_id', 'request']
)


@receiver(cart_processed)
def on_cart_deleted(sender, cart, payment_method_id, request, **kwargs):
    if not cart.checkout_details:
        # If the cart has not checkout details, it can be normally deleted.
        return

    if cart.has_changed():
        # If the cart has changed, need to be checked-out before continue.
        raise CheckoutNeeded

    # Process payment


    # Add items to acquired lists
    items_acquired.send(sender=sender, cart=cart, request=request)

    # Create payment object
    payment = Payment.objects.create_payment(cart=cart, payment_intent=payment_intent)
    # Send payment confirmation email
    cart_record = payment.cart_record
    user = payment.user

    if payment.amount > 0:
        payment_successful.send(
            sender=sender, user=user, request=request, cart_record=cart_record
        )
