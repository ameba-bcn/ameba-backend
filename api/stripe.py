from django.conf import settings
import stripe
from stripe.error import InvalidRequestError

import api.exceptions as api_exceptions
import api.models as api_models
import api.signals.items as items

# Authenticate stripe
stripe.api_key = settings.STRIPE_SECRET

CURRENCY = 'eur'
PAYMENT_METHOD_TYPES = ['card']
EMPTY_PAYMENT_INTENT_ID = 'empty_payment'
EMPTY_INVOICE_ID = 'empty_payment'
EMPTY_PAYMENT_SECRET = 'empty_payment'


class IntentStatus:
    SUCCESS = 'succeeded'
    NOT_NEEDED = 'no_payment_needed'


EMPTY_PAYMENT_INTENT = {
    'payment_intent': {'status': IntentStatus.SUCCESS},
    'client_secret': EMPTY_PAYMENT_SECRET,
    'status': IntentStatus.NOT_NEEDED,
    'amount': 0,
    'id': EMPTY_PAYMENT_INTENT_ID
}

EMPTY_INVOICE = {
    'id': 'empty_invoice',
    'status': 'paid',
    'amount_due': 0,
    'payment_intent_id': EMPTY_PAYMENT_INTENT_ID
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
    elif price.recurring and price.recurring.interval != period:
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
        invoice = stripe.Invoice.retrieve(subscription.latest_invoice)
        break
    else:
        invoice = stripe.Invoice.create(**invoice_props)

    if invoice.status == 'draft':
        return invoice.finalize_invoice()

    return invoice


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


def _attach_payment_method(customer_id, payment_method_id):
    stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)


def update_payment_method(user, payment_method_id):
    customer = _get_or_create_customer(user.id, user.username)
    _attach_payment_method(customer.id, payment_method_id)


def get_invoice(invoice_id):
    return stripe.Invoice.retrieve(invoice_id)


def get_or_create_invoice(cart):
    if hasattr(cart, 'payment') and cart.payment is not None:
        invoice_id = cart.payment.invoice['id']
        invoice = get_invoice(invoice_id)
    else:
        invoice = create_invoice(
            user=cart.user,
            cart_items=cart.get_cart_items()
        )
    return invoice


def _get_customer_payment_methods(customer_id):
    return stripe.PaymentMethod.list(type='card', customer=customer_id)


def _check_payment_methods_are_same(pm_1, pm_2):
    return pm_1['card']['fingerprint'] == pm_2['card']['fingerprint']


def _check_user_pm_exists(customer_id, pm):
    for user_pm in _get_customer_payment_methods(customer_id)['data']:
        if _check_payment_methods_are_same(pm, user_pm):
            return user_pm
    return False


def get_or_create_user_pm(user, card_number, exp_month, exp_year, cvc):
    customer = _get_or_create_customer(user.id, user.username)
    card_data = dict(
        number=card_number, exp_month=exp_month, exp_year=exp_year, cvc=cvc
    )
    new_pm = stripe.PaymentMethod.create(type='card', card=card_data)
    if user_pm := _check_user_pm_exists(customer.id, new_pm):
        return user_pm
    _attach_payment_method(customer.id, new_pm.id)
    return new_pm


def get_payment_method_id(user, pm_id):
    new_pm = stripe.PaymentMethod.retrieve(pm_id)
    if user_pm := _check_user_pm_exists(user.id, new_pm):
        return user_pm.id
    _attach_payment_method(user.id, new_pm.id)
    return new_pm.id


def _try_to_pay(invoice, payment_method_id):
    if payment_method_id:
        invoice = invoice.pay(payment_method=payment_method_id)
    else:
        invoice = invoice.finalize_invoice()
    return invoice


def get_or_create_payment(cart):
    # If cart has changed or never checked out
    if cart.checkout_hash is None or cart.has_changed():
        raise api_exceptions.CheckoutNeeded
    # If cart has payment but hashes doesn't match
    if hasattr(cart, 'payment') and cart.payment and cart.checkout_hash != \
        cart.payment.cart_hash:
        cart.payment.delete()
    # If cart has payment and hashes match
    elif hasattr(cart, 'payment') and cart.payment and cart.checkout_hash ==\
        cart.payment.cart_hash:
        return cart.payment
    # When payment must be created
    invoice = get_or_create_invoice(cart) if cart.amount > 0 else None
    payment = api_models.Payment.objects.get_or_create_payment(
        cart=cart, invoice=invoice
    )

    if payment.amount == 0:
        if payment.close():
            payment.refresh_from_db()

    return payment


def get_payment_intent(payment_intent_id):
    return stripe.PaymentIntent.retrieve(payment_intent_id)


def _get_user_from_customer_id(customer):
    if customer.isdigit() and api_models.User.objects.filter(id=customer):
        return api_models.User.objects.get(int(customer))


def _get_item_variants_from_id(invoice):
    for line in invoice.lines['data']:
        item_variant_id = line['price']['product']
        iv_matches = api_models.ItemVariant.objects.filter(id=item_variant_id)
        if iv_matches:
            yield iv_matches[0]


def _create_payment_from_invoice(invoice):
    user = _get_user_from_customer_id(invoice.customer)
    payment = api_models.Payment.objects.get_or_create_payment(
        user=user, invoice=invoice
    )
    for item_variant in _get_item_variants_from_id(invoice):
        payment.item_variants.add(item_variant)
    return payment


def get_payment_from_invoice(invoice):
    payments = api_models.Payment.objects.filter(invoice_id=invoice.id)
    if payments:
        return payments[0]
    return _create_payment_from_invoice(invoice)
