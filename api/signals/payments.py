from django.dispatch import receiver
from api.signals.items import items_acquired
import django.dispatch as dispatch


payment_attempt = dispatch.Signal(providing_args=['payment'])


@receiver(payment_attempt)
def on_successful_payment(sender, payment, **kwargs):
    cart = payment.cart
    # Finish payment
    payment.close_payment()

