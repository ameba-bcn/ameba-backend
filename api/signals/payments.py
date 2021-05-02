import django.dispatch
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from api.stripe import get_payment_intent, get_create_update_payment_intent,\
    InvalidRequestError, IntentStatus, NO_PAYMENT_NEEDED_ID
from api.models import Payment, Cart
from api.exceptions import StripeSyncError, CheckoutNeeded, PaymentIsNotSucceed
from api.email_factories import PaymentSuccessfulEmail


cart_checkout = django.dispatch.Signal(providing_args=['cart'])
cart_processed = django.dispatch.Signal(providing_args=['cart', 'request'])

SUCCEEDED_PAYMENTS = [IntentStatus.SUCCESS, IntentStatus.NOT_NEEDED]


@receiver(cart_checkout)
def sync_payment_intent(sender, cart, request, **kwargs):
    try:
        checkout_details = {"date_time": str(timezone.now())}
        if cart.amount > 0:
            payment_intent = get_create_update_payment_intent(
                amount=cart.amount,
                idempotency_key=cart.id,
                checkout_details=cart.checkout_details
            )
            checkout_details['payment_intent'] = payment_intent

        cart.checkout_details = checkout_details
        cart.save()

    except InvalidRequestError as StripeError:
        if not cart.checkout_details:
            cart.checkout_details = {}
        cart.checkout_details['error'] = {
            'message': StripeError.user_message,
            'code': StripeError.code
        }
        cart.save()
        raise StripeSyncError(
            detail=StripeError.user_message,
            code=f'stripe_error_{StripeError.code}'
        )


@receiver(cart_processed)
def on_cart_deleted(sender, cart, request, **kwargs):
    if not cart.checkout_details:
        return

    if not cart.is_checkout_updated():
        raise CheckoutNeeded

    payment_intent = get_payment_intent(checkout_details=cart.checkout_details)

    if payment_intent['status'] not in SUCCEEDED_PAYMENTS and not settings.DEBUG:
        raise PaymentIsNotSucceed

    payment = Payment.objects.create_payment(cart=cart, payment_intent=payment_intent)
    # Send payment confirmation email
    cart_record = payment.cart_record
    user = payment.user
    email = PaymentSuccessfulEmail.from_request(
        request=request, cart_record=cart_record, user=user
    )
    email.send()
