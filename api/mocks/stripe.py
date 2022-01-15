import sys
import types
import unittest.mock as mock
import logging
import stripe
import time

this_module = sys.modules[__name__]

# module_name = 'stripe'
# stripe = types.ModuleType(module_name)
# sys.modules[module_name] = stripe


class Errors:
    InvalidRequestError = Exception
    SignatureVerificationError = Exception


class BaseMock:
    objects = {}

    def __init__(self, id, **kwargs):
        self.id = str(id)
        self.created = time.time()
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def retrieve(cls, id):
        try:
            return cls.objects[id]
        except KeyError:
            raise Errors.InvalidRequestError

    @classmethod
    def list(cls, **kwargs):
        result = {'data': []}
        for element in cls.objects.values():
            for key, value in kwargs.items():
                if not hasattr(element, key) or getattr(element, key).id != value:
                    break
            else:
                result['data'].append(element)
        return result

    @classmethod
    def create(cls, id=None, **kwargs):
        if not id:
            if not cls.objects:
                id = 0
            else:
                id = max(map(lambda x: int(x), cls.objects.keys())) + 1
                id = str(id)
        cls.objects[id] = cls(id=id, **kwargs)
        return cls.retrieve(id=id)

    def __getattribute__(self, item):
        try:
            object_id = super().__getattribute__(item + '_id')
        except:
            return super().__getattribute__(item)
        class_name = item.capitalize() + 'Mock'
        return getattr(this_module, class_name).retrieve(object_id)

    def __getitem__(self, item):
        return getattr(self, item)


class ProductMock(BaseMock):
    objects = {}

    def __init__(self, id, name, active=True):
        super().__init__(id=id, name=name, active=active)


class PriceMock(BaseMock):
    objects = {}

    def __init__(self, id, currency, product, unit_amount, recurring):
        self.product_id = product
        super().__init__(id=id, currency=currency, unit_amount=unit_amount,
                         recurring=recurring)


class CustomerMock(BaseMock):
    objects = {}

    def __init__(self, id, name):
        super().__init__(id=id, name=name)


class SubscriptionMock(BaseMock):
    objects = {}

    def __init__(self, id, customer, items, payment_behaviour):
        self.customer_id = customer
        super().__init__(id=id, items=items,payment_behaviour=payment_behaviour)


class InvoiceItemMock(BaseMock):
    objects = {}

    def __init__(self, id, customer, price):
        self.price_id = price
        super().__init__(id=id, customer=customer, price=price)


class InvoiceMock(BaseMock):
    objects = {}

    def __init__(self, id, customer, collection_method):
        self.customer_id = customer
        self.status = 'draft'
        super().__init__(id=id, collection_method=collection_method)

    def finalize_invoice(self):
        self.status = 'open'


class WebhookMock:

    @staticmethod
    def construct_event(payload, *args, **kwargs):
        return payload


def mock_stripe_succeeded_payment(client, url, invoice):
    headers = {'HTTP_STRIPE_SIGNATURE': 'stripe-signature'}
    invoice['status'] = 'paid'
    data = {
        'type': 'invoice.payment_succeeded',
        'data': {
            'object': invoice
        }
    }
    return client.post(url, data=data, **headers)


logging.info('Mocking stripe module ...')
stripe.Product = ProductMock
stripe.Price = PriceMock
stripe.Customer = CustomerMock
stripe.Subscription = SubscriptionMock
stripe.InvoiceItem = InvoiceItemMock
stripe.Invoice = InvoiceMock
stripe.PaymentMethod = mock.MagicMock()
stripe.PaymentIntent = mock.MagicMock()
stripe.Webhook = WebhookMock
stripe.error = Errors
