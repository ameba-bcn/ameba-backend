from datetime import timedelta
from django.db.models import Sum
from django.db import models


EXPIRE_HOURS_BEFORE_EVENT = 1
EXPIRE_BEFORE_EVENT = timedelta(hours=EXPIRE_HOURS_BEFORE_EVENT)


ARTICLE = 'article'
SUBSCRIPTION = 'subscription'
EVENT = 'event'

ITEM_TYPES = (
    (ARTICLE, 'Article'),
    (SUBSCRIPTION, 'Subscription'),
    (EVENT, 'Event')
)


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=1000)
    images = models.ManyToManyField(to='Image', blank=False)
    acquired_by = models.ManyToManyField(to='User', blank=True,
                                         related_name='acquired_items')
    saved_by = models.ManyToManyField(to='User', blank=True,
                                      related_name='saved_items')
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def price_range(self):
        prices = set(variant.price for variant in self.variants.all())
        if len(prices) == 1:
            return f'{min(prices)}€'
        elif len(prices) == 0:
            return '-'
        return f'{min(prices)}€ / {max(prices)}€'

    def __str__(self):
        return self.name

    def get_max_discount_value(self, user, code=None):
        """ Get max discount value among valid discounts for given user
        :param user: models.User
        :return: Integer with max of the applicable discounts for given user
        """
        vd = list(map(lambda x: x.value, self.get_valid_discounts(user, code)))
        # Has valid discounts
        if vd:
            return max(vd)
        return 0

    def get_valid_discounts(self, user, code=None):
        """
        Get valid discounts for given user.
        :param user: models.User
        :param code: models.DiscountCode id
        :return: Generator
        """
        for discount in self.discounts.all():
            if (
                (discount.need_code and code and discount == code.discount)
                or not discount.need_code
            ):
                if discount.check_user_applies(user, code):
                    yield discount

    @property
    def stock(self):
        if -1 in [variant.stock for variant in self.variants.all()]:
            return -1
        return self.variants.aggregate(Sum('stock'))['stock__sum']

    @property
    def has_stock(self):
        return bool(self.stock)

    def is_subscription(self):
        return hasattr(self, 'subscription')


class ItemAttributeType(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class ItemAttribute(models.Model):
    attribute = models.ForeignKey(
        'ItemAttributeType', on_delete=models.CASCADE
    )
    value = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.attribute.name}: {self.value}'


class ItemVariant(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE,
                             related_name='variants')
    attributes = models.ManyToManyField('ItemAttribute', blank=False)
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    benefits = models.TextField(max_length=1000, default='')

    def get_valid_discounts(self, user, code=None):
        return self.item.get_valid_discounts(user, code)

    def get_max_discount_value(self, user, code=None):
        return self.item.get_max_discount_value(user, code)

    @property
    def amount(self):
        """ Returns price in lower EUR currency unit (cents)
        :return: Integer with price in EUR cents
        """
        return int(float(self.price) * 100)

    @property
    def name(self):
        item_name = self.item.name
        attrs = self.attributes.all()
        variants = [f'{attr.attribute.name}={attr.value}' for attr in attrs]
        return f'{item_name}(' + ','.join(variants) + ')'

    def __str__(self):
        return self.name
