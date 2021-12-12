from django.dispatch import receiver
from api.signals.items import items_acquired
from api.signals.emails import payment_closed
import django.dispatch as dispatch


payment_attempt = dispatch.Signal(providing_args=['payment'])


@receiver(payment_attempt)
def on_successful_payment(sender, payment, **kwargs):
    cart = payment.cart
    # Update payment object
    payment.update_invoice()
    # Add items to acquired lists
    items_acquired.send(sender=sender, cart=cart)
    # Finish payment
    payment.finish_payment()
    payment_closed.send(sender=sender, cart=cart)
