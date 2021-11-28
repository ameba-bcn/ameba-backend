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
    'payment_intent': {'status': IntentStatus.SUCCESS},
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


def get_or_create_product(identifier, name):
    try:
        stripe_product = stripe.Product.retrieve(id=str(identifier))
    except stripe.error.InvalidRequestError as err:
        stripe_product = stripe.Product.create(
            id=str(identifier), name=name
        )
    return stripe_product


def _get_product_price(product_id):
    prices = sorted(
        stripe.Price.list(product=product_id)['data'], key=lambda x: x['created']
    )
    if not prices:
        return None
    return prices[-1]


def get_update_or_create_price(product, amount, period='year'):
    price = _get_product_price(product)
    if not price or price.unit_amount != amount:
        return stripe.Price.create(
            currency=CURRENCY,
            product=product,
            unit_amount=amount,
            recurring=dict(interval=period)
        )
    return price


def create_or_update_product_and_price(identifier, name, amount):
    stripe_product = get_or_create_product(identifier, name)
    stripe_price = get_update_or_create_price(identifier, amount)
    return stripe_product, stripe_price


def _get_or_create_customer(customer_id, name):
    try:
        customer = stripe.Customer.retrieve(id=str(customer_id))
    except stripe.error.InvalidRequestError as err:
        customer = stripe.Customer.create(id=str(customer_id), name=name)
    return customer


def _get_stripe_subscription_id(item_variant_id, user_id):
    return f'{item_variant_id}-{user_id}'


def _get_or_create_subscription(product_id, customer_id):
    try:
        subscription = stripe.Subscription.retrieve(id=str(product_id))
    except stripe.error.InvalidRequestError as err:
        prices = [{'price': _get_product_price(product_id)}]
        subscription = stripe.Subscription.create(
            id=_get_stripe_subscription_id(product_id, customer_id),
            customer=str(customer_id),
            items=prices,
            payment_behavior='default_incomplete'
        )
    return subscription


def _create_invoice_item(customer_id, price_id):
    return stripe.InvoiceItem.create(customer=customer_id, price=price_id)


def create_invoice(user, cart_items):
    """ Only 1 subscription allowed in cart_items!!
    :param cart_items: item variants with discounts related to same cart
    :param user: owner of the cart
    :return:
    """
    customer = _get_or_create_customer(customer_id=user.id, name=user.username)
    invoice_props = dict(
        customer=customer.id,
        collection_method='charge_automatically'
    )
    for cart_item in cart_items:
        product = stripe.Product.retrieve(id=cart_item.item_variant.id)
        if cart_item.item_variant.interval:
            subscription = _get_or_create_subscription(
                product_id=product.id,
                customer_id=customer.id
            )
            invoice_props['subscription'] = subscription.id
        price = _get_product_price(product_id=cart_item.item_variant.id)
        _create_invoice_item(customer_id=customer.id, price_id=price.id)
    return stripe.Invoice.create(**invoice_props)
