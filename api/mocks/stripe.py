import sys
import json
import time

this_module = sys.modules[__name__]


class error:
    InvalidRequestError = Exception
    SignatureVerificationError = Exception


class BaseMock:
    objects = {}

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
            raise error.InvalidRequestError

    @classmethod
    def list(cls, **kwargs):
        result = {'data': []}
        for element in cls.objects.values():
            for key, value in kwargs.items():
                if not hasattr(element, key) or getattr(element, key) != value:
                    break
            else:
                result['data'].append(element)
        return result

    @classmethod
    def create(cls, id=None, **kwargs):
        if not id:
            if not cls.objects:
                id = '0'
            else:
                id = max(map(lambda x: int(x), cls.objects.keys())) + 1
                id = str(id)
        cls.objects[id] = cls(id=id, **kwargs)
        return cls.retrieve(id=id)

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


class Customer(BaseMock):
    objects = {}

    def __init__(self, id, name):
        super().__init__(id=id, name=name)


class Subscription(BaseMock):
    objects = {}

    def __init__(self, id, customer, items, payment_behavior):
        self.customer = customer
        self.latest_invoice = self.create_invoice(customer, items)
        super().__init__(
            id=id, items=items, payment_behavior=payment_behavior
        )

    @staticmethod
    def create_invoice(customer, items):
        for item in items:
            InvoiceItem.create(customer=customer, price=item['price']['id'])
        return Invoice.create(customer=customer)['id']


class InvoiceItem(BaseMock):
    objects = {}

    def __init__(self, id, customer, price):
        self.price_id = price
        super().__init__(id=id, customer=customer)


class PaymentIntent(BaseMock):
    objects = {}

    def __init__(self, id):
        self.client_secret = 'adcf44bg5bfcadcgb5fgb2c44c3gbafd'
        super().__init__(id=id)


class Invoice(BaseMock):
    objects = {}

    def __init__(self, id, customer, collection_method='charge_automatically'):
        self.customer = customer
        self.amount_due = 0
        self.status = 'draft'
        self.lines = {'data': []}
        self.payment_intent = PaymentIntent.create()['id']
        self.get_lines_and_amount()
        super().__init__(id=id, collection_method=collection_method)

    def finalize_invoice(self):
        self.status = 'open'
        return self

    def get_lines_and_amount(self):
        for id in list(InvoiceItem.objects.keys()):
            obj = InvoiceItem.objects[id]
            if obj.customer == self.customer:
                self.lines['data'].append(obj)
                self.amount_due += obj.price.unit_amount
                InvoiceItem.objects.pop(id)


class Webhook:

    @staticmethod
    def construct_event(payload, *args, **kwargs):
        return json.loads(payload)


def mock_stripe_succeeded_payment(client, url, invoice):
    headers = {'HTTP_STRIPE_SIGNATURE': 'stripe-signature'}
    invoice['status'] = 'paid'
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
