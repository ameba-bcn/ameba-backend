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


def get_create_update_payment_intent(amount, idempotency_key, checkout_details):
    if checkout_details and checkout_details["payment_intent"]["id"]:
        intent_id = checkout_details["payment_intent"]["id"]
        checkout_details = stripe.PaymentIntent.retrieve(id=intent_id)
        checkout_details.update({"amount": amount})
        checkout_details.save()
    else:
        checkout_details = create_payment_intent(
            amount=amount, idempotency_key=str(idempotency_key)
        )
    return checkout_details


def get_payment_intent(checkout_details):
    if checkout_details and checkout_details["payment_intent"]["id"]:
        pid = checkout_details["payment_intent"]["id"]
        if pid == NO_PAYMENT_NEEDED_ID:
            return EMPTY_PAYMENT_INTENT
        payment_intent = stripe.PaymentIntent.retrieve(id=pid)
        return payment_intent
    elif not checkout_details or "payment_intent" not in checkout_details:
        raise CartCheckoutNotProcessed
    else:
        raise WrongPaymentIntent
