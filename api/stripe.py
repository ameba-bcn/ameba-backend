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


def _get_or_create_product(product_id, product_name):
    try:
        stripe_product = stripe.Product.retrieve(id=str(product_id))
        if stripe_product.name != product_name:
            stripe_product.update({'name': product_name})
    except stripe.error.InvalidRequestError as err:
        stripe_product = stripe.Product.create(
            id=str(product_id), name=product_name
        )
    return stripe_product


def _get_product_price(product_id):
    prices = sorted(
        stripe.Price.list(product=product_id)['data'], key=lambda x: x['created']
    )
    if not prices:
        return None
    return prices[-1]


def _is_price_changed(price, amount, period):
    if price.unit_amount != amount:
        return True
    elif bool(price.recurring) is not bool(period):
        return True
    elif price.recurring and price.recurring.period != period:
        return True
    return False


def _get_update_or_create_price(product_id, amount, period):
    price = _get_product_price(product_id)
    if not price or _is_price_changed(price, amount, period):
        return stripe.Price.create(
            currency=CURRENCY,
            product=product_id,
            unit_amount=amount,
            recurring=dict(interval=period)
        )
    return price


def create_or_update_product_and_price(item_variant):
    product_id = item_variant.id
    period = item_variant.get_recurrence()
    product_name = item_variant.name
    stripe_product = _get_or_create_product(product_id, product_name)
    stripe_price = _get_update_or_create_price(
        product_id, item_variant.amount, period
    )
    return stripe_product, stripe_price


def _get_or_create_customer(customer_id, name):
    try:
        customer = stripe.Customer.retrieve(id=str(customer_id))
    except stripe.error.InvalidRequestError as err:
        customer = stripe.Customer.create(id=str(customer_id), name=name)
    return customer


def _get_stripe_subscription_id(product_id, customer_id):
    return f'{product_id}-{customer_id}'


def _create_subscription(product_id, customer_id):
    prices = [{'price': _get_product_price(product_id)}]
    subscription = stripe.Subscription.create(
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
    cart_items = list(cart_items)
    regular_items = filter(
        lambda x: x.item_variant.get_recurrence() is None, cart_items
    )
    subscriptions = filter(
        lambda x: x.item_variant.get_recurrence(), cart_items
    )
    for cart_item in regular_items:
        price = _get_product_price(product_id=cart_item.item_variant.id)
        _create_invoice_item(customer_id=customer.id, price_id=price.id)

    for cart_item in subscriptions:
        subscription = _create_subscription(
            product_id=cart_item.item_variant.id,
            customer_id=customer.id
        )
        return stripe.Invoice.retrieve(subscription.latest_invoice)

    return stripe.Invoice.create(**invoice_props)


def create_payment_method(number, exp_month, exp_year, cvc):
    return stripe.PaymentMethod.create(
        type='card',
        card=dict(
            number=number,
            exp_month=exp_month,
            exp_year=exp_year,
            cvc=cvc
        )
    ).id


def attach_payment_method(customer_id, payment_method_id):
    stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)


def update_payment_method(user, payment_method_id):
    customer = _get_or_create_customer(user.id, user.username)
    attach_payment_method(customer.id, payment_method_id)
