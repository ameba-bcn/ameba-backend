import logging
import sys
import time

from django.conf import settings
from django.db import transaction

import api.exceptions as api_exceptions
import api.models as api_models


logger = logging.getLogger(__name__)


def mock_stripe():
    testing = sys.argv[1:2] == ['test']
    return testing or not settings.STRIPE_SECRET or not settings.STRIPE_PUBLIC


if mock_stripe():
    import api.mocks.stripe as stripe
else:
    import stripe


# Authenticate stripe
stripe.api_key = settings.STRIPE_SECRET
# Pin the API version explicitly. The Stripe account default (and the webhook
# endpoint) are on 2020-08-27; pinning here means a change of the account
# default in the Dashboard can never silently change the shape of the objects
# this code reads (invoice.payment_intent, invoice.subscription, ...).
STRIPE_API_VERSION = '2020-08-27'
stripe.api_version = STRIPE_API_VERSION
# stripe-python retries network failures with an automatic Idempotency-Key, so
# a retried POST never creates a duplicate object.
stripe.max_network_retries = 2

CURRENCY = 'eur'
PAYMENT_METHOD_TYPES = ['card']
EMPTY_PAYMENT_INTENT_ID = 'empty_payment'
EMPTY_INVOICE_ID = 'empty_payment'
EMPTY_PAYMENT_SECRET = 'empty_payment'

# PaymentIntent statuses in which the customer can still (re)try to pay the
# very same PaymentIntent, so its client_secret can be handed out again.
REUSABLE_INTENT_STATUSES = (
    'requires_payment_method', 'requires_confirmation', 'requires_action',
)
# The customer already paid (or the payment is being processed by the bank):
# never void these, just hand the same client_secret back.
IN_FLIGHT_INTENT_STATUSES = ('processing', 'succeeded')

# Subscriptions in these statuses are still being (re)charged by Stripe. Once
# the member buys a new membership they must be canceled, otherwise the member
# could be charged twice (see cancel_previous_subscriptions). 'incomplete' is
# deliberately not here: Stripe never charges those on its own (they expire
# after 23h) and the subscription just paid could still be reported as such.
STALE_SUBSCRIPTION_STATUSES = ('past_due', 'unpaid')


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


SHIPPING_PRODUCT_ID = 'shipping-surcharge'
# Keep this in sync with api.models.cart.SHIPPING_SURCHARGE_CENTS — the cart's
# displayed total and this Stripe-charged amount must never diverge.
SHIPPING_SURCHARGE_CENTS = 700


def _get_or_create_shipping_price():
    _get_or_create_product(SHIPPING_PRODUCT_ID, 'Envío')
    return _get_update_or_create_price(
        SHIPPING_PRODUCT_ID, SHIPPING_SURCHARGE_CENTS, None
    )


def create_or_update_product_and_price(item_variant):
    product_id = str(item_variant.id)
    period = item_variant.get_recurrence()
    product_name = item_variant.name
    stripe_product = _get_or_create_product(product_id, product_name)
    stripe_price = _get_update_or_create_price(
        product_id, item_variant.amount, period
    )
    return stripe_product, stripe_price


def _get_or_create_customer(customer_id, name, email):
    try:
        customer = stripe.Customer.retrieve(id=str(customer_id))
    except stripe.error.InvalidRequestError as err:
        customer = stripe.Customer.create(
            id=str(customer_id), name=name, email=email
        )
    return customer


def _get_stripe_subscription_id(product_id, customer_id):
    return f'{product_id}-{customer_id}'


def _field(stripe_object, name):
    """ Reads an optional field of a Stripe object (or of a test mock). """
    try:
        return stripe_object[name]
    except (KeyError, AttributeError):
        return None


def _idempotency_kwargs(idempotency_key, suffix):
    if not idempotency_key:
        return {}
    return {'idempotency_key': f'{idempotency_key}:{suffix}'}


def _create_subscription(customer_id, prices, coupon_id=None,
                         add_invoice_items=None, metadata=None,
                         idempotency_key=None):
    subscription_attrs = dict(
        customer=str(customer_id),
        items=prices,
        payment_behavior='default_incomplete'
    )
    if coupon_id:
        subscription_attrs['coupon'] = coupon_id
    if add_invoice_items:
        # One-off lines (tickets, shop items, shipping) bought together with
        # the membership go on the subscription's first invoice explicitly,
        # instead of being left as "pending" invoice items on the customer.
        subscription_attrs['add_invoice_items'] = add_invoice_items
    if metadata:
        subscription_attrs['metadata'] = metadata
    subscription_attrs.update(
        _idempotency_kwargs(idempotency_key, 'subscription')
    )
    subscription = stripe.Subscription.create(**subscription_attrs)
    return subscription


def _get_discount_name(cart):
    cart_discounts = cart.get_cart_items_with_discounts()
    discounts = set(
        d['discount'].name for d in cart_discounts if d['discount']
    )
    return ', '.join(discounts)


def _create_discount_coupon(cart, idempotency_key=None):
    """ Creates a one-time coupon worth the cart discount, or None if the cart
    has no discount. The coupon is deleted right after being applied (an
    already applied discount survives the coupon deletion).
    """
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
    coupon_attrs.update(_idempotency_kwargs(idempotency_key, 'coupon'))
    return stripe.Coupon.create(**coupon_attrs)


def _delete_coupon(coupon_id):
    try:
        stripe.Coupon.delete(coupon_id)
    except Exception:
        logger.exception('Could not delete temporary coupon %s', coupon_id)


def _get_product_and_prices(cart):
    products = {}
    for item_variant in cart.item_variants.all():
        product, price = create_or_update_product_and_price(item_variant)
        products[product.id] = {'product': product, 'price': price}
    return products


def _setup_future_payments(invoice):
    """ Only for memberships: the card used for the first payment is kept
    for the yearly renewals (off-session charges)."""
    pi = stripe.PaymentIntent.retrieve(invoice['payment_intent'])
    stripe.PaymentIntent.modify(pi.id, setup_future_usage='off_session')


def _cleanup_failed_invoice_creation(created):
    """ Best effort: undo whatever was created in Stripe for a checkout
    attempt that failed half way, so nothing is left pending on the customer
    (which Stripe would otherwise sweep into the next invoice)."""
    for item_id in created['invoice_items']:
        try:
            stripe.InvoiceItem.delete(item_id)
        except Exception:
            logger.exception('Cleanup: could not delete invoice item %s',
                             item_id)
    if created['subscription']:
        try:
            # Canceling an incomplete subscription voids its first invoice.
            stripe.Subscription.delete(created['subscription'])
        except Exception:
            logger.exception('Cleanup: could not cancel subscription %s',
                             created['subscription'])
    if created['invoice']:
        try:
            invoice = stripe.Invoice.retrieve(created['invoice'])
            if invoice['status'] == 'draft':
                stripe.Invoice.delete(created['invoice'])
            elif invoice['status'] == 'open':
                stripe.Invoice.void_invoice(created['invoice'])
        except Exception:
            logger.exception('Cleanup: could not discard invoice %s',
                             created['invoice'])


def create_invoice_from_cart(cart, idempotency_key=None):
    """ Creates (and finalizes) the Stripe invoice to be paid for this cart.
    Only 1 subscription allowed in cart_items!!

    - Carts with a membership create an incomplete subscription; its first
      invoice also carries the one-off lines of the cart.
    - Any other cart creates a one-off invoice with auto_advance=False, so
      Stripe never tries to charge it on its own: it is only paid when the
      customer confirms its PaymentIntent from the checkout page.
    - Invoice items are always attached to their own invoice (never left
      pending on the customer, where Stripe would add them to whatever
      invoice is created next for that customer).

    :param cart: cart with discounts related to same cart
    :param idempotency_key: base Stripe idempotency key for this attempt
    :return: finalized invoice
    """
    user = cart.user
    created = {'invoice_items': [], 'invoice': None, 'subscription': None}
    coupon = None
    log_ctx = {'cart_id': str(cart.id), 'user_id': user.id}
    try:
        customer = _get_or_create_customer(
            customer_id=user.id, name=user.username, email=user.email
        )
        products = _get_product_and_prices(cart=cart)
        coupon = _create_discount_coupon(cart, idempotency_key)

        cart_items = list(cart.get_cart_items())
        one_off_prices = [
            products[str(ci.item_variant.id)]['price'].id
            for ci in cart_items if ci.item_variant.get_recurrence() is None
        ]
        if cart.delivery_method == 'shipping':
            one_off_prices.append(_get_or_create_shipping_price().id)
        subscription_items = [
            ci for ci in cart_items if ci.item_variant.get_recurrence()
        ]
        metadata = {'cart_id': str(cart.id)}

        if subscription_items:
            product_id = str(subscription_items[0].item_variant.id)
            subscription = _create_subscription(
                customer_id=customer.id,
                prices=[{'price': products[product_id]['price'].id}],
                coupon_id=coupon.id if coupon else None,
                add_invoice_items=[{'price': p} for p in one_off_prices],
                metadata=metadata,
                idempotency_key=idempotency_key,
            )
            created['subscription'] = subscription.id
            invoice = stripe.Invoice.retrieve(subscription.latest_invoice)
            logger.info('Stripe subscription %s created (invoice %s) %s',
                        subscription.id, invoice.id, log_ctx)
        else:
            invoice_attrs = dict(
                customer=customer.id,
                collection_method='charge_automatically',
                auto_advance=False,
                pending_invoice_items_behavior='exclude',
                metadata=metadata,
            )
            if coupon:
                invoice_attrs['discounts'] = [{'coupon': coupon.id}]
            invoice_attrs.update(
                _idempotency_kwargs(idempotency_key, 'invoice')
            )
            invoice = stripe.Invoice.create(**invoice_attrs)
            created['invoice'] = invoice.id
            for index, price_id in enumerate(one_off_prices):
                item = stripe.InvoiceItem.create(
                    customer=customer.id, price=price_id, invoice=invoice.id,
                    **_idempotency_kwargs(idempotency_key, f'item-{index}')
                )
                created['invoice_items'].append(item.id)
            # Re-read: a replayed idempotent create returns the original
            # (draft) response even if the invoice was finalized since.
            invoice = stripe.Invoice.retrieve(invoice.id)
            logger.info('Stripe invoice %s created %s', invoice.id, log_ctx)

        if invoice.status == 'draft':
            invoice = invoice.finalize_invoice()
        # From here on the items belong to a finalized invoice: voiding the
        # invoice is the cleanup, not deleting the items.
        created['invoice_items'] = []

        if subscription_items:
            _setup_future_payments(invoice)
    except Exception:
        logger.exception('Stripe invoice creation failed, cleaning up %s %s',
                         created, log_ctx)
        _cleanup_failed_invoice_creation(created)
        raise
    finally:
        if coupon:
            _delete_coupon(coupon.id)

    logger.info('Stripe invoice %s finalized, payment_intent %s %s',
                invoice.id, invoice.payment_intent, log_ctx)
    return invoice


def discard_invoice(invoice):
    """ Makes an unpaid invoice unpayable so it is never charged: an
    incomplete subscription is canceled (which voids its invoice), a draft is
    deleted and an open one-off invoice is voided. Paid / void invoices are
    left untouched.
    :return: True if the invoice is (now) unpayable, False if it is paid.
    """
    status = invoice['status']
    if status == 'paid':
        return False
    if status in ('void', 'uncollectible'):
        return True
    subscription_id = _field(invoice, 'subscription')
    if subscription_id:
        subscription = stripe.Subscription.retrieve(subscription_id)
        if subscription['status'] in ('incomplete', 'incomplete_expired'):
            if subscription['status'] == 'incomplete':
                stripe.Subscription.delete(subscription_id)
            logger.info('Canceled incomplete subscription %s (invoice %s)',
                        subscription_id, invoice['id'])
            return True
        # Never cancel an active/renewing subscription from here.
        logger.warning('Not discarding invoice %s: subscription %s is %s',
                       invoice['id'], subscription_id,
                       subscription['status'])
        return True
    if status == 'draft':
        stripe.Invoice.delete(invoice['id'])
    elif status == 'open':
        stripe.Invoice.void_invoice(invoice['id'])
    logger.info('Discarded %s invoice %s', status, invoice['id'])
    return True


def _attach_payment_method(customer_id, payment_method_id):
    stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)


def update_payment_method(user, payment_method_id):
    customer = _get_or_create_customer(user.id, user.username, user.email)
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
    customer = _get_or_create_customer(user.id, user.username, user.email)
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


# --------------------------------------------------------------------------
# Cart -> Payment
# --------------------------------------------------------------------------

def _payment_idempotency_key(cart, fingerprint):
    """ Stripe idempotency key for one checkout attempt of a cart: same cart
    + same contents + same attempt number => same Stripe objects. The attempt
    counter is bumped whenever a previous attempt is discarded or failed, so
    a retry after a cleanup (or going back to a previous cart content) gets
    fresh objects instead of Stripe replaying the discarded ones."""
    attempt = (cart.checkout_details or {}).get('payment_attempts', 0)
    return f'cart-{cart.id}-{fingerprint[:24]}-a{attempt}'


def _bump_payment_attempt(cart):
    details = dict(cart.checkout_details or {})
    details['payment_attempts'] = details.get('payment_attempts', 0) + 1
    cart.checkout_details = details
    api_models.Cart.objects.filter(pk=cart.pk).update(checkout_details=details)


def _get_intent_status(invoice):
    if not invoice or not invoice['payment_intent']:
        return None
    try:
        return get_payment_intent(invoice['payment_intent'])['status']
    except stripe.error.InvalidRequestError:
        return None


def _resolve_existing_payment(cart, payment, fingerprint):
    """ Decides what to do with the payment already attached to the cart.
    :return: the payment to hand back to the client, or None if a new one
             must be created (the old one has been discarded and detached).
    """
    log_ctx = {'cart_id': str(cart.id), 'payment_id': str(payment.id),
               'invoice_id': payment.invoice_id}
    invoice = find_invoice(payment.invoice_id) if payment.invoice_id else None

    if invoice is not None and invoice['status'] == 'paid':
        # Paid but the webhook has not arrived yet: fulfil it now (idempotent)
        logger.info('Existing payment already paid, fulfilling %s', log_ctx)
        payment.close()
        return payment

    same_contents = (payment.details or {}).get('cart_fingerprint') \
        == fingerprint
    intent_status = _get_intent_status(invoice)

    if intent_status in IN_FLIGHT_INTENT_STATUSES:
        if not same_contents:
            logger.warning('Cart changed while its payment is %s %s',
                           intent_status, log_ctx)
            raise api_exceptions.PaymentInProgress
        payment.update_details()
        return payment

    if (
        same_contents and invoice is not None
        and invoice['status'] == 'open'
        and intent_status in REUSABLE_INTENT_STATUSES
    ):
        logger.info('Reusing open invoice for unchanged cart %s', log_ctx)
        payment.update_details()
        payment.refresh_cart_record()
        return payment

    # Contents changed, or the invoice / PaymentIntent is no longer usable
    logger.info('Discarding previous payment (same_contents=%s, '
                'invoice_status=%s, intent_status=%s) %s', same_contents,
                invoice and invoice['status'], intent_status, log_ctx)
    if invoice is not None and not discard_invoice(invoice):
        # Got paid between the two Stripe calls
        payment.close()
        return payment
    payment.update_details()
    payment.detach_cart(delete=False)
    _bump_payment_attempt(cart)
    return None


def get_or_create_cart_payment(cart):
    """ Returns the Payment the customer has to pay for this cart.

    Calling it again for an unchanged cart returns the same Payment (same
    PaymentIntent / client_secret). If the cart contents changed, the old
    invoice is voided and a new one is created. The cart is NOT deleted here:
    it is consumed only when the payment succeeds (Payment.close()).

    The cart row is locked for the whole operation so concurrent calls for
    the same cart are serialized (the second one reuses the first's payment).
    """
    error = None
    with transaction.atomic():
        cart = api_models.Cart.objects.select_for_update().get(pk=cart.pk)

        # If cart has changed or never checked out
        if not cart.checkout_hash or cart.has_changed():
            raise api_exceptions.CheckoutNeeded

        fingerprint = cart.get_payment_fingerprint()
        existing = api_models.Payment.objects.select_for_update().filter(
            cart=cart, processed=False
        ).first()
        if existing is not None:
            payment = _resolve_existing_payment(cart, existing, fingerprint)
            if payment is not None:
                return payment

        if cart.amount <= 0:
            # Free cart: closed (fulfilled) straight away
            return api_models.Payment.objects.create_payment(
                cart=cart, invoice=None, fingerprint=fingerprint
            )

        idempotency_key = _payment_idempotency_key(cart, fingerprint)
        invoice = None
        try:
            with transaction.atomic():
                invoice = create_invoice_from_cart(
                    cart, idempotency_key=idempotency_key
                )
                payment = api_models.Payment.objects.create_payment(
                    cart=cart, invoice=invoice, fingerprint=fingerprint
                )
        except Exception as exc:
            error = exc
            if invoice is not None:
                # The invoice exists in Stripe but the local Payment could
                # not be saved: make sure it can never be charged.
                try:
                    discard_invoice(invoice)
                except Exception:
                    logger.exception('Could not discard orphan invoice %s',
                                     invoice.id)
            # Next attempt must not replay the objects just discarded.
            _bump_payment_attempt(cart)
    if error is not None:
        raise error
    logger.info('Payment %s created for cart %s (invoice %s, '
                'payment_intent %s)', payment.id, cart.id, payment.invoice_id,
                payment.payment_intent_id)
    return payment


def settle_cart_payment_if_paid(cart):
    """ If the cart has a pending payment that has been paid in Stripe but
    whose webhook has not been processed yet, fulfil it now. Lets the
    frontend see the cart consumed right after paying, without waiting for
    the webhook. Never raises: Stripe being down must not break the cart.
    :return: True if the cart has been consumed by a paid payment.
    """
    payment = api_models.Payment.objects.filter(
        cart=cart, processed=False
    ).exclude(invoice_id=None).first()
    if payment is None:
        return False
    try:
        invoice = find_invoice(payment.invoice_id)
        if invoice is None or invoice['status'] != 'paid':
            return False
        fulfil_invoice_payment(invoice)
        return True
    except Exception:
        logger.exception('Could not settle pending payment %s of cart %s',
                         payment.id, cart.id)
        return False


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
    """ Returns the local Payment of a Stripe invoice (creating it for
    invoices generated by Stripe itself, i.e. membership renewals), locked
    for update. Must be called inside a transaction.

    The customer's user row is locked first so two concurrent deliveries of
    the same event can't both create a Payment for the same invoice.
    """
    customer = str(invoice['customer'])
    if customer.isdigit():
        list(api_models.User.objects.select_for_update().filter(id=customer))
    payment = api_models.Payment.objects.select_for_update().filter(
        invoice_id=invoice['id']
    ).order_by('timestamp').first()
    if payment is not None:
        return payment
    return _create_payment_from_invoice(invoice)


def fulfil_invoice_payment(invoice):
    """ Idempotent fulfilment of a paid invoice: whoever gets here first
    (webhook, payment endpoint or cart read) hands the items over; the rest
    find the payment already processed. """
    with transaction.atomic():
        payment = get_payment_from_invoice(invoice)
        if payment.processed:
            logger.info('Payment %s (invoice %s) already processed',
                        payment.id, invoice['id'])
            return payment
        payment.close()
        return payment


def cancel_subscription(invoice):
    invoice_lines = invoice['lines']['data']
    # Cancel subscription
    for il in invoice_lines:
        if il['type'] == 'subscription':
            stripe.Subscription.delete(il['subscription'])
            return True
    return False


def cancel_previous_subscriptions(user, subscription):
    """ Called once a membership has been bought: cancels the customer's
    other Stripe subscriptions so only the new one keeps charging:
    - active subscriptions of a different membership type (upgrade), and
    - any past_due / unpaid subscription (e.g. a failed renewal still being
      retried by Stripe), which would otherwise charge the member twice.
    The active subscription of the membership just bought is kept.
    """
    subs_variants = [str(var.id) for var in subscription.variants.all()]
    try:
        stripe_subs = stripe.Subscription.list(customer=str(user.id))
        for stripe_sub in stripe_subs['data']:
            status = stripe_sub['status']
            if status in STALE_SUBSCRIPTION_STATUSES:
                logger.info('Canceling %s subscription %s of user %s',
                            status, stripe_sub['id'], user.id)
                stripe.Subscription.delete(stripe_sub['id'])
                continue
            if status == 'active':
                for stripe_sub_item in stripe_sub['items']['data']:
                    if stripe_sub_item['price']['product'] not in subs_variants:
                        logger.info('Canceling previous subscription %s of '
                                    'user %s', stripe_sub_item['subscription'],
                                    user.id)
                        stripe.Subscription.delete(
                            stripe_sub_item['subscription']
                        )
                        break
    except stripe.error.InvalidRequestError:
        logger.exception('Could not cancel previous subscriptions of user %s',
                         user.id)


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
    if 'customer' not in payment_intent:
        return
    customer_id = payment_intent['customer']
    payment_method_id = payment_intent['payment_method']
    stripe.Customer.modify(
        customer_id,
        invoice_settings={'default_payment_method': payment_method_id}
    )


def iter_stale_open_manual_invoices(older_than_days):
    """ Open one-off (non subscription) invoices created more than
    `older_than_days` days ago. Used by the void_stale_invoices command. """
    cutoff = int(time.time()) - int(older_than_days) * 24 * 3600
    invoices = stripe.Invoice.list(
        status='open', created={'lt': cutoff}, limit=100
    )
    if hasattr(invoices, 'auto_paging_iter'):
        invoices = invoices.auto_paging_iter()
    else:
        invoices = invoices['data']
    for invoice in invoices:
        if invoice['created'] >= cutoff:
            continue
        if _field(invoice, 'subscription'):
            continue
        yield invoice


def void_invoice(invoice_id):
    return stripe.Invoice.void_invoice(invoice_id)
