import sys
import types
import unittest.mock as mock
import django.conf as conf

this_module = sys.modules[__name__]

module_name = 'stripe'
module = types.ModuleType(module_name)
sys.modules[module_name] = module


class BaseMock:
    objects = {}

    def __init__(self, id, **kwargs):
        self.id = id
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def retrieve(cls, id):
        return cls.objects[id]

    @classmethod
    def create(cls, id=None, **kwargs):
        if not id:
            id = len(cls.objects) + 1
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

    def __init__(self, id, name, active=True):
        super().__init__(id=id, name=name, active=active)


class PriceMock(BaseMock):

    def __init__(self, id, currency, product, unit_amount, recurring):
        self.product_id = product
        super().__init__(id=id, currency=currency, unit_amount=unit_amount,
                         recurring=recurring)


class CustomerMock(BaseMock):

    def __init__(self, id, name):
        super().__init__(id=id, name=name)


class SubscriptionMock(BaseMock):

    def __init__(self, id, customer, items, payment_behaviour):
        self.customer_id = customer
        super().__init__(id=id, items=items,payment_behaviour=payment_behaviour)


class InvoiceItemMock(BaseMock):

    def __init__(self, id, customer, price):
        self.price_id = price
        super().__init__(id=id, customer=customer, price=price)


class InvoiceMock(BaseMock):

    def __init__(self, id, customer, collection_method):
        self.customer_id = customer
        super().__init__(id=id, collection_method=collection_method)


module.Product = ProductMock
module.Price = PriceMock
module.Customer = CustomerMock
module.Subscription = SubscriptionMock
module.InvoiceItem = InvoiceItemMock
module.Invoice = InvoiceMock
module.PaymentMethod = mock.MagicMock()
module.PaymentIntent = mock.MagicMock()
