import django.dispatch
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from api.stripe import get_payment_intent, get_create_update_payment_intent,\
    InvalidRequestError
from api.models import Payment, Cart
from api.exceptions import StripeSyncError


cart_checkout = django.dispatch.Signal(providing_args=['cart'])


@receiver(cart_checkout)
def sync_payment_intent(sender, cart, request, **kwargs):
    try:
        payment_intent = get_create_update_payment_intent(
            amount=cart.amount,
            idempotency_key=cart.id,
            checkout_details=cart.checkout_details
        )
        cart.checkout_details = {
            "payment_intent": payment_intent
        }
        cart.save()
    except InvalidRequestError as StripeError:
        raise StripeSyncError(
            detail=StripeError.user_message,
            code=f'stripe_error_{StripeError.code}'
        )


@receiver(pre_delete, sender=Cart)
def on_cart_deleted(instance, **kwargs):
    payment_intent = get_payment_intent(checkout_details=instance.checkout_details)
    Payment.objects.create_payment(cart=instance, payment_intent=payment_intent)
