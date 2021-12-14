from django.dispatch import receiver
import django.dispatch as dispatch


payment_successful = dispatch.Signal(providing_args=['payment'])


@receiver(payment_successful)
def on_successful_payment(sender, payment, **kwargs):
    # Finish payment
    payment.close_payment()

