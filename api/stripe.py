import sys
from django.conf import settings
from stripe.error import InvalidRequestError

import api.exceptions as api_exceptions
import api.models as api_models


def mock_stripe():
    testing = sys.argv[1:2] == ['test']
    return testing or not settings.STRIPE_SECRET or not settings.STRIPE_PUBLIC


if mock_stripe():
    import api.mocks.stripe as stripe
else:
    import stripe


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
    product_id = str(item_variant.id)
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


def _create_subscription(customer_id, prices, coupon_id=None):
    subscription_attrs = dict(
        customer=str(customer_id),
        items=prices,
        payment_behavior='default_incomplete'
    )
    if coupon_id:
        subscription_attrs['coupon'] = coupon_id
    subscription = stripe.Subscription.create(**subscription_attrs)
    return subscription


def _create_invoice_item(customer_id, price_id):
    return stripe.InvoiceItem.create(customer=customer_id, price=price_id)


def _get_discount_name(cart):
    cart_discounts = cart.get_cart_items_with_discounts()
    discounts = set(
        d['discount'].name for d in cart_discounts if d['discount']
    )
    return ', '.join(discounts)


def _get_discounts_attr(cart):
    # Compute invoice discounts
    amount_off = cart.base_amount - cart.amount
    if amount_off <= 0:
        return None

    coupon_attrs = {
        'amount_off': amount_off,
        'name': _get_discount_name(cart),
        'currency': 'eur',
        'applies_to': {
            'products': [str(iv.id) for iv in cart.item_variants.all()]
        }
    }
    coupon = stripe.Coupon.create(**coupon_attrs)
    return [{'coupon': coupon.id}]


def _delete_discounts(discounts):
    for discount in discounts:
        stripe.Coupon.delete(discount['coupon'])


def _get_product_and_prices(cart):
    products = {}
    for item_variant in cart.item_variants.all():
        product, price = create_or_update_product_and_price(item_variant)
        products[product.id] = {'product': product, 'price': price}
    return products


def _setup_future_payments(invoice):
    pi = stripe.PaymentIntent.retrieve(invoice['payment_intent'])
    stripe.PaymentIntent.modify(pi.id, setup_future_usage='off_session')


def create_invoice_from_cart(cart):
    """ Only 1 subscription allowed in cart_items!!
    :param cart: cart with discounts related to same cart
    :return:
    """
    user = cart.user
    customer = _get_or_create_customer(customer_id=user.id, name=user.username)
    products = _get_product_and_prices(cart=cart)
    discounts = _get_discounts_attr(cart)
    invoice_props = dict(
        customer=customer.id,
        discounts=discounts,
        collection_method='charge_automatically',
        payment_settings={'payment_method_types': PAYMENT_METHOD_TYPES}
    )

    cart_items = list(cart.get_cart_items())
    regular_items = filter(
        lambda x: x.item_variant.get_recurrence() is None, cart_items
    )
    subscriptions = filter(
        lambda x: x.item_variant.get_recurrence(), cart_items
    )
    for cart_item in regular_items:
        price = products[str(cart_item.item_variant.id)]['price']
        _create_invoice_item(customer_id=customer.id, price_id=price.id)

    for cart_item in subscriptions:
        product_id = str(cart_item.item_variant.id)
        subscription = _create_subscription(
            customer_id=customer.id,
            prices=[{'price': products[product_id]['price']}],
            coupon_id=discounts[0]['coupon'] if discounts else None
        )
        invoice = stripe.Invoice.retrieve(subscription.latest_invoice)
        break
    else:
        invoice = stripe.Invoice.create(**invoice_props)

    if invoice.status == 'draft':
        invoice = invoice.finalize_invoice()

    _setup_future_payments(invoice)

    if discounts:
        _delete_discounts(discounts)
    return invoice


def _attach_payment_method(customer_id, payment_method_id):
    stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)


def update_payment_method(user, payment_method_id):
    customer = _get_or_create_customer(user.id, user.username)
    _attach_payment_method(customer.id, payment_method_id)


def find_invoice(invoice_id):
    try:
        return stripe.Invoice.retrieve(invoice_id)
    except stripe.error.InvalidRequestError:
        return None


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


def create_payment_and_destroy_cart(cart):
    # If cart has changed or never checked out
    if cart.checkout_hash is None or cart.has_changed():
        raise api_exceptions.CheckoutNeeded

    invoice = create_invoice_from_cart(cart) if cart.amount > 0 else None
    payment = api_models.Payment.objects.create_payment(
        cart=cart, invoice=invoice
    )

    return payment


def get_payment_intent(payment_intent_id):
    return stripe.PaymentIntent.retrieve(payment_intent_id)


def _get_user_from_customer_id(customer):
    if customer.isdigit() and api_models.User.objects.filter(id=customer):
        return api_models.User.objects.get(id=customer)


def _gen_item_variants_from_id(invoice):
    for line in invoice['lines']['data']:
        item_variant_id = line['price']['product']
        iv_matches = api_models.ItemVariant.objects.filter(id=item_variant_id)
        if iv_matches:
            yield iv_matches.first()


def _create_payment_from_invoice(invoice):
    user = _get_user_from_customer_id(invoice['customer'])
    item_variants = _gen_item_variants_from_id(invoice)
    payment = api_models.Payment.objects.create_payment(
        user=user, invoice=invoice, item_variants=item_variants
    )
    return payment


def get_payment_from_invoice(invoice):
    payments = api_models.Payment.objects.filter(invoice_id=invoice['id'])
    if payments:
        return payments[0]
    return _create_payment_from_invoice(invoice)


def cancel_subscription(invoice):
    invoice_lines = invoice['lines']['data']
    # Cancel subscription
    for il in invoice_lines:
        if il['type'] == 'subscription':
            stripe.Subscription.delete(il['subscription'])
            return True
    return False


def cancel_previous_subscriptions(user, subscription):
    subs_variants = [str(var.id) for var in subscription.variants.all()]
    try:
        stripe_subs = stripe.Subscription.list(customer=str(user.id))
        for stripe_sub in stripe_subs['data']:
            if stripe_sub['status'] == 'active':
                for stripe_sub_item in stripe_sub['items']['data']:
                    if stripe_sub_item['price']['product'] not in subs_variants:
                        stripe.Subscription.delete(
                            stripe_sub_item['subscription']
                        )
    except stripe.error.InvalidRequestError:
        pass


def get_user_stored_cards(user):
    card_data = []
    try:
        cards = stripe.Customer.list_payment_methods(
            str(user.id),
            type='card'
        )
    except stripe.error.InvalidRequestError:
        return card_data

    for card in cards['data']:
        card_id = card['id']
        exp = f"{card['card']['exp_year']}/{card['card']['exp_month']}"
        last4 = card['card']['last4']
        brand = card['card']['brand']
        card_data.append(dict(exp=exp, last4=last4, brand=brand, id=card_id))
    return card_data


def set_payment_method_default(payment_intent):
    customer_id = payment_intent['customer']
    payment_method_id = payment_intent['payment_method']
    stripe.Customer.modify(
        customer_id,
        invoice_settings={'default_payment_method': payment_method_id}
    )
