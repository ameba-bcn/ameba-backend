from datetime import timedelta, datetime

from django.db import models
from django.db.models import Sum


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
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()
    type = models.CharField(max_length=25, choices=ITEM_TYPES)
    date = models.DateTimeField(blank=True, null=True)
    is_expired = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def expire(self):
        self.is_expired = True
        self.save()

    def get_is_expired(self):
        if self.date and datetime.now() > self.date - EXPIRE_BEFORE_EVENT:
            self.expire()
        return self.is_expired

    def get_stock(self):
        if stock := self.variants.aggregate(Sum('stock'))['stock__sum'] > 0:
            return stock
        else:
            return self.stock

    def __str__(self):
        return self.name

    def get_discount(self, user):
        """ Discount logic for a given item and user
        :param user: models.User
        :param item: models.Item
        :return: models.Discount
        """
        discounts = [0]
        for discount in self.discounts.all():
            if discount.check_user_applies(user):
                discounts.append(discount.value)
        return max(discounts)


class ItemImage(models.Model):
    item = models.ForeignKey(to=Item, on_delete=models.DO_NOTHING,
                             related_name='images')
    image = models.ImageField(upload_to='items')
    active = models.BooleanField(default=True)

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        return self.image.name


class ItemVariant(models.Model):
    name = models.CharField(max_length=25)
    item = models.ForeignKey(
        to=Item, on_delete=models.DO_NOTHING, related_name='variants'
    )
    stock = models.IntegerField()
    description = models.TextField(max_length=1000, blank=True)
    image = models.ImageField(blank=True, upload_to='items')

    def get_description(self):
        if self.description:
            return self.description
        else:
            return self.item.description

    def __str__(self):
        return self.name
