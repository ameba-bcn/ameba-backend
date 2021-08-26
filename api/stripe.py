from django.conf import settings
import stripe
from stripe.error import InvalidRequestError

from api.exceptions import WrongPaymentIntent, CartCheckoutNotProcessed

# Authenticate stripe
stripe.api_key = settings.STRIPE_SECRET

CURRENCY = 'eur'
PAYMENT_METHOD_TYPES = ['card']
NO_PAYMENT_NEEDED_ID = 'nopaymentneeded'


class IntentStatus:
    SUCCESS = 'succeeded'
    NOT_NEEDED = 'no_payment_needed'


EMPTY_PAYMENT_INTENT = {
    'status': IntentStatus.NOT_NEEDED,
    'amount': 0,
    'id': NO_PAYMENT_NEEDED_ID
}


def create_payment_intent(amount, idempotency_key):
    return stripe.PaymentIntent.create(
        amount=amount,
        currency=CURRENCY,
        payment_method_types=PAYMENT_METHOD_TYPES,
        idempotency_key=idempotency_key
    )


def payment_intent_exists(checkout_details):
    return (
        checkout_details
        and 'id' in checkout_details.get('payment_intent', {})
    )


def no_payment_intent_needed(checkout_details):
    return (
        checkout_details
        and 'date_time' in checkout_details
        and 'payment_intent' not in checkout_details
    )


def get_create_update_payment_intent(amount, idempotency_key, checkout_details):
    if payment_intent_exists(checkout_details):
        intent_id = checkout_details["payment_intent"]["id"]
        payment_intent = stripe.PaymentIntent.retrieve(id=intent_id)
        payment_intent.update({"amount": amount})
        payment_intent.save()
    else:
        payment_intent = create_payment_intent(
            amount=amount, idempotency_key=str(idempotency_key)
        )
    return payment_intent


def get_payment_intent(checkout_details):
    if payment_intent_exists(checkout_details):
        pid = checkout_details["payment_intent"]["id"]
        try:
            payment_intent = stripe.PaymentIntent.retrieve(id=pid)
            return payment_intent
        except stripe.error.InvalidRequestError:
            raise WrongPaymentIntent
    elif no_payment_intent_needed(checkout_details):
        return EMPTY_PAYMENT_INTENT
    else:
        raise WrongPaymentIntent
