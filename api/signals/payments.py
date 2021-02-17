import django.dispatch
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save

from api.stripe import get_payment_intent, get_create_update_payment_intent,\
    InvalidRequestError
from api.models import Payment, Cart, Subscription, Membership
from api.exceptions import StripeSyncError
from api.stripe import IntentStatus
from api.exceptions import PaymentIsNotSucceed

cart_checkout = django.dispatch.Signal(providing_args=['cart'])
cart_deletion = django.dispatch.Signal(providing_args=['cart'])


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


def resolve_ameba_membership(cart):
    for item in cart.items.all():
        if isinstance(item, Subscription):
            Membership.objects.create_membership(
                user=cart.user, subscription=item
            )


def is_payment_success(payment_intent):
    return payment_intent['status'] == IntentStatus.SUCCESS


@receiver(cart_deletion)
def on_cart_deleted(cart, **kwargs):
    payment_intent = get_payment_intent(
        checkout_details=cart.checkout_details
    )
    if not is_payment_success(payment_intent):
        raise PaymentIsNotSucceed

    Payment.objects.create_payment(
        cart=cart, payment_intent=payment_intent
    )
    resolve_ameba_membership(cart)
