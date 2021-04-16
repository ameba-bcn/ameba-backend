import django.dispatch
from django.dispatch import receiver
from django.conf import settings

from api.stripe import get_payment_intent, get_create_update_payment_intent,\
    InvalidRequestError, IntentStatus
from api.models import Payment, Cart
from api.exceptions import StripeSyncError
from api.email_factories import PaymentSuccessfulEmail


cart_checkout = django.dispatch.Signal(providing_args=['cart'])
cart_processed = django.dispatch.Signal(providing_args=['cart', 'request'])


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


@receiver(cart_processed)
def on_cart_deleted(sender, cart, request, **kwargs):
    payment_intent = get_payment_intent(checkout_details=cart.checkout_details)
    payment = Payment.objects.create_payment(
        cart=cart, payment_intent=payment_intent
    )

    # Handle email notifications here
    if payment.status == IntentStatus.SUCCESS or settings.DEBUG:
        # Send payment confirmation email
        cart_record = payment.cart_record
        user = payment.user
        email = PaymentSuccessfulEmail.from_request(
            request=request, cart_record=cart_record, user=user
        )
        email.send()
