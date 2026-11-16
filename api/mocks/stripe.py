import sys
import json
import time

this_module = sys.modules[__name__]


class error:
    InvalidRequestError = Exception
    SignatureVerificationError = Exception


# Module level config set by api.stripe (ignored by the mock)
api_key = None
api_version = None
max_network_retries = 0

# Every Stripe call made through the mock, as (ClassName.method, kwargs).
# Tests can inspect it; reset it with `calls.clear()`.
calls = []


class BaseMock:
    objects = {}
    # idempotency_key -> object id: replaying a key returns the original
    # object, like Stripe does.
    idempotency = {}

    def __init__(self, id, **kwargs):
        self.id = str(id)
        self.created = time.time()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __iter__(self):
        for key, value in self.to_dict().items():
            yield key, value

    def _serialize_element(self, element):
        if type(element) in (list, dict, tuple):
            return self._serialize(element)
        elif issubclass(element.__class__, BaseMock):
            return element.to_dict()
        else:
            return element

    def _serialize(self, iterable):
        if type(iterable) in (list, tuple):
            new_list = []
            for el in iterable:
                new_list.append(self._serialize_element(el))
            return new_list
        elif type(iterable) is dict:
            new_dict = {}
            for key, value in iterable.items():
                new_dict[key] = self._serialize_element(value)
            return new_dict

    def to_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if key.endswith('_id'):
                r_key = key.replace('_id', '')
                d[r_key] = getattr(self, r_key)
        d.update(self.__dict__)
        return self._serialize(d)

    @classmethod
    def retrieve(cls, id):
        try:
            return cls.objects[id]
        except KeyError:
            raise error.InvalidRequestError(
                f"{cls.__name__} with id={id} doesn't exist."
            )

    @classmethod
    def list(cls, **kwargs):
        kwargs.pop('limit', None)
        result = {'data': []}
        for element in cls.objects.values():
            for key, value in kwargs.items():
                if isinstance(value, dict):
                    # range filters, e.g. created={'lt': ts}
                    current = getattr(element, key, None)
                    if 'lt' in value and not current < value['lt']:
                        break
                    continue
                if not hasattr(element, key) or getattr(element, key) != value:
                    break
            else:
                result['data'].append(element)
        return result

    @classmethod
    def create(cls, id=None, idempotency_key=None, **kwargs):
        calls.append((f'{cls.__name__}.create', kwargs))
        if idempotency_key and idempotency_key in cls.idempotency:
            # Stripe replays the original response for a reused key
            return cls.objects.get(cls.idempotency[idempotency_key]) \
                or cls(id=cls.idempotency[idempotency_key], **kwargs)
        if not id:
            if not cls.objects:
                id = '0'
            else:
                numeric_ids = filter(lambda x: x.isdigit(), cls.objects.keys())
                id = max(map(lambda x: int(x), numeric_ids)) + 1
                id = str(id)
        cls.objects[id] = cls(id=id, **kwargs)
        if idempotency_key:
            cls.idempotency[idempotency_key] = id
        return cls.retrieve(id=id)

    @classmethod
    def delete(cls, id):
        calls.append((f'{cls.__name__}.delete', {'id': id}))
        return bool(cls.objects.pop(id, None))

    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

    @classmethod
    def modify(cls, id, **kwargs):
        calls.append((f'{cls.__name__}.modify', dict(kwargs, id=id)))
        for key, value in kwargs.items():
            cls.objects[id][key] = value

    def __getattribute__(self, item):
        try:
            object_id = super().__getattribute__(item + '_id')
        except AttributeError:
            return super().__getattribute__(item)
        class_name = item.capitalize()
        return getattr(this_module, class_name).retrieve(object_id)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Product(BaseMock):
    objects = {}

    def __init__(self, id, name, active=True):
        super().__init__(id=id, name=name, active=active)


class PriceRecurring(BaseMock):
    pass


class Price(BaseMock):
    objects = {}

    def __init__(self, id, currency, product, unit_amount, recurring):
        self.recurring = PriceRecurring.create(**recurring)
        super().__init__(
            id=id, currency=currency, unit_amount=unit_amount, product=product
        )


class Coupon(BaseMock):
    objects = {}

    def __init__(self, id, amount_off, name, currency, applies_to):
        super().__init__(
            id=id,
            amount_off=amount_off,
            name=name,
            currency=currency,
            applies_to=applies_to
        )


class Customer(BaseMock):
    objects = {}

    def __init__(self, id, name, email):
        super().__init__(id=id, name=name, email=email)

    @classmethod
    def list_payment_methods(cls, id, type, **kargs):
        exp_year = '2022'
        exp_month = '06'
        last4 = '4242'
        brand = 'visa'
        card_id = 'pm_1EUp2m2tXu0CfXKwKWi2bboc'
        return dict(
            data=[dict(
                card=dict(exp_year=exp_year, exp_month=exp_month, last4=last4,
                          brand=brand),
                id=card_id
            )]
        )


def _price_id(price):
    return price if isinstance(price, str) else price['id']


class Subscription(BaseMock):
    objects = {}
    idempotency = {}

    def __init__(self, id, customer, items, payment_behavior, coupon=None,
                 add_invoice_items=None, metadata=None):
        self.customer = customer
        # payment_behavior='default_incomplete': incomplete until the first
        # invoice is paid (see mock_stripe_succeeded_payment)
        self.status = 'incomplete'
        self.latest_invoice = self.create_invoice(
            id, customer, items, add_invoice_items or []
        )
        items = [
            {'price': Price.retrieve(_price_id(item['price'])),
             'subscription': id}
            for item in items
        ]
        items = {'data': items}
        super().__init__(
            id=id, items=items, payment_behavior=payment_behavior,
            coupon=coupon, metadata=metadata
        )

    @staticmethod
    def create_invoice(subscription_id, customer, items, add_invoice_items):
        invoice = Invoice.create(
            customer=customer, subscription=subscription_id,
            billing_reason='subscription_create',
            pending_invoice_items_behavior='exclude'
        )
        for item in list(items) + list(add_invoice_items):
            InvoiceItem.create(
                customer=customer, price=_price_id(item['price']),
                invoice=invoice.id
            )
        return invoice['id']

    @classmethod
    def delete(cls, id):
        """ Canceling an incomplete subscription voids its open invoice """
        calls.append(('Subscription.delete', {'id': id}))
        subscription = cls.objects.get(id)
        if subscription is None:
            return False
        invoice = Invoice.objects.get(subscription.latest_invoice)
        if invoice is not None and invoice.status in ('draft', 'open'):
            invoice.status = 'void'
        subscription.status = 'canceled'
        cls.objects.pop(id)
        return True


class InvoiceItem(BaseMock):
    objects = {}
    idempotency = {}

    def __init__(self, id, customer, price, invoice=None):
        self.price_id = price
        super().__init__(id=id, customer=customer)
        self.invoice = invoice
        if invoice is not None:
            # Attached straight to its invoice (never left pending)
            target = Invoice.retrieve(invoice)
            if target.status != 'draft':
                raise error.InvalidRequestError(
                    f'Invoice {invoice} is not a draft.'
                )
            target.lines['data'].append(self)
            target.amount_due += self.price.unit_amount


class PaymentIntent(BaseMock):
    objects = {}
    idempotency = {}

    def __init__(self, id, customer=None):
        # Unique per PaymentIntent, so tests can tell a reused payment from a
        # new one.
        self.client_secret = f'pi_{id}_secret_mock'
        self.payment_method = 'asdoasdoijasdoisajdasdoijsa'
        self.customer = customer
        self.status = 'requires_payment_method'
        self.setup_future_usage = None
        super().__init__(id=id)


class Invoice(BaseMock):
    objects = {}
    idempotency = {}

    def __init__(
        self, id, customer, collection_method='charge_automatically',
        pending_invoice_items_behavior='include', **kwargs
    ):
        self.customer = customer
        self.amount_due = 0
        self.status = 'draft'
        self.subscription = None
        self.billing_reason = 'manual'
        self.lines = {'data': []}
        self.payment_intent = PaymentIntent.create(customer=customer)['id']
        if pending_invoice_items_behavior != 'exclude':
            self.get_lines_and_amount()
        super().__init__(
            id=id, collection_method=collection_method,
            pending_invoice_items_behavior=pending_invoice_items_behavior,
            **kwargs
        )

    def finalize_invoice(self):
        calls.append(('Invoice.finalize_invoice', {'id': self.id}))
        if self.status == 'draft':
            self.status = 'open'
        return self

    @classmethod
    def void_invoice(cls, id):
        calls.append(('Invoice.void_invoice', {'id': id}))
        invoice = cls.retrieve(id)
        if invoice.status != 'open':
            raise error.InvalidRequestError(
                f'Invoice {id} is {invoice.status}, can not be voided.'
            )
        invoice.status = 'void'
        intent = PaymentIntent.objects.get(invoice.payment_intent)
        if intent is not None:
            intent.status = 'canceled'
        return invoice

    def get_lines_and_amount(self):
        for id in list(InvoiceItem.objects.keys()):
            obj = InvoiceItem.objects[id]
            if obj.customer == self.customer and obj.invoice is None:
                self.lines['data'].append(obj)
                self.amount_due += obj.price.unit_amount
                InvoiceItem.objects.pop(id)


class Webhook:

    @staticmethod
    def construct_event(payload, *args, **kwargs):
        return json.loads(payload)


def mark_invoice_paid(invoice_id):
    """ What Stripe does when the customer pays an invoice's PaymentIntent """
    invoice = Invoice.retrieve(invoice_id)
    invoice.status = 'paid'
    intent = PaymentIntent.objects.get(invoice.payment_intent)
    if intent is not None:
        intent.status = 'succeeded'
    if invoice.subscription and invoice.subscription in Subscription.objects:
        Subscription.objects[invoice.subscription].status = 'active'
    return invoice


def mock_stripe_succeeded_payment(client, url, invoice):
    headers = {'HTTP_STRIPE_SIGNATURE': 'stripe-signature'}
    invoice['status'] = 'paid'
    if not isinstance(invoice, dict) and invoice.id in Invoice.objects:
        mark_invoice_paid(invoice.id)
    data = {
        'type': 'invoice.payment_succeeded',
        'data': {
            'object': invoice if type(invoice) is dict else invoice.to_dict()
        }
    }
    return client.post(url, data=data, format='json', **headers)


def mock_stripe_failed_payment(client, url, invoice):
    headers = {'HTTP_STRIPE_SIGNATURE': 'stripe-signature'}
    invoice['status'] = 'open'
    data = {
        'type': 'invoice.payment_failed',
        'data': {
            'object': invoice if type(invoice) is dict else invoice.to_dict()
        }
    }
    return client.post(url, data=data, format='json', **headers)

