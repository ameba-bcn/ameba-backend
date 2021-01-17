from datetime import timedelta

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
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()
    images = models.ManyToManyField(to='Image', blank=False)
    acquired_by = models.ManyToManyField(to='User', blank=True,
                                         related_name='acquired_items')
    saved_by = models.ManyToManyField(to='User', blank=True,
                                      related_name='saved_items')
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_max_discount_value(self, user):
        """ Get max discount value among valid discounts for given user
        :param user: models.User
        :return: Integer with max of the applicable discounts for given user
        """
        vd = list(map(lambda x: x.value, self.get_valid_discounts(user)))
        # Has valid discounts
        if vd:
            return max(vd)
        return 0

    def get_valid_discounts(self, user):
        """
        Get valid discounts for given user.
        :param user: models.User
        :return: Generator
        """
        for discount in self.discounts.all():
            if discount.check_user_applies(user):
                yield discount

