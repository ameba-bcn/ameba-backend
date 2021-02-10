from django.conf import settings
import stripe

# Authenticate stripe
stripe.api_key = settings.STRIPE_SECRET

CURRENCY = 'eur'
PAYMENT_METHOD_TYPES = ['card']


def create_payment_intent(amount, unique_key):
    return stripe.PaymentIntent.create(
        amount=amount,
        currency=CURRENCY,
        payment_method_types=PAYMENT_METHOD_TYPES,
        idempotency_key=unique_key
    )


