import django.dispatch
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from api.stripe import get_payment_intent, get_create_update_payment_intent,\
    InvalidRequestError
from api.models import Payment
from api.models.cart import cart_checkout
from api.exceptions import StripeSyncError, CheckoutNeeded, PaymentIsNotSucceed
from api.email_factories import PaymentSuccessfulEmail
from api.signals.memberships import subscription_purchased
from api.signals.items import items_acquired


cart_processed = django.dispatch.Signal(providing_args=['cart', 'request'])


@receiver(cart_checkout)
def sync_payment_intent(sender, cart, **kwargs):
    try:
        checkout_details = {"date_time": str(timezone.now())}
        if cart.amount > 0:
            payment_intent = get_create_update_payment_intent(
                amount=cart.amount,
                idempotency_key=cart.id,
                checkout_details=cart.checkout_details
            )
            checkout_details['payment_intent'] = payment_intent
        cart.set_checkout_details(checkout_details)

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
        # If the cart has not checkout details, it can be normally deleted.
        return

    if cart.has_changed():
        # If the cart has changed, need to be checked-out before continue.
        raise CheckoutNeeded

    payment_intent = get_payment_intent(checkout_details=cart.checkout_details)

    if type(cart.checkout_details) is dict:
        cart.checkout_details['payment_intent'] = payment_intent
    else:
        cart.checkout_details = {'payment_intent': payment_intent}
    cart.save()

    if not cart.is_payment_succeeded():
        raise PaymentIsNotSucceed

    # Reach here if the payment has been succeeded.
    if cart.subscription:
        subscription_purchased.send(
            sender=sender,
            member=cart.user.member,
            subscription=cart.subscription
        )
    # Add items to acquired lists
    items_acquired.send(sender=sender, cart=cart)

    # Create payment object
    payment = Payment.objects.create_payment(cart=cart, payment_intent=payment_intent)
    # Send payment confirmation email
    cart_record = payment.cart_record
    user = payment.user
    email = PaymentSuccessfulEmail.from_request(
        request=request, cart_record=cart_record, user=user
    )
    email.send()
