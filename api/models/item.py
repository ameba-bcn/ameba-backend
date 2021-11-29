from datetime import timedelta

from django.conf import settings
from django.db.models import Sum
from django.db import models
from django.utils.translation import gettext as _

EXPIRE_HOURS_BEFORE_EVENT = 1
EXPIRE_BEFORE_EVENT = timedelta(hours=EXPIRE_HOURS_BEFORE_EVENT)


INTERVALS = (
    ('year', 'year'),
)


if settings.DEBUG:
    INTERVALS = (
        ('year', 'year'),
        ('minute', 'minute'),
    )


class Item(models.Model):
    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    name = models.CharField(
        max_length=100, unique=True, verbose_name=_('name')
    )
    description = models.TextField(
        max_length=1000, verbose_name=_('description')
    )
    images = models.ManyToManyField(
        to='Image', blank=False, verbose_name=_('images')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))
    saved_by = models.ManyToManyField(
        to='User', blank=True, related_name='saved_items',
        verbose_name=_('saved by')
    )

    @property
    def acquired_by(self):
        return ItemVariant.acquired_by.through.objects.filter(
            itemvariant__in=self.variants.all()
        ).select_related('user')

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

    def is_article(self):
        return hasattr(self, 'article')

    def is_event(self):
        return hasattr(self, 'event')


class ItemAttributeType(models.Model):
    class Meta:
        verbose_name = _('Item attribute type')
        verbose_name_plural = _('Item attribute types')

    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class ItemAttribute(models.Model):
    class Meta:
        verbose_name = _('Item attribute')
        verbose_name_plural = _('Item attributes')

    attribute = models.ForeignKey(
        'ItemAttributeType', on_delete=models.CASCADE, verbose_name=_(
            'attribute'
        )
    )
    value = models.CharField(max_length=15, verbose_name=_('value'))

    def __str__(self):
        return f'{self.attribute.name}: {self.value}'


class ItemVariant(models.Model):
    class Meta:
        verbose_name = _('Item variant')
        verbose_name_plural = _('Item variants')

    item = models.ForeignKey('Item', on_delete=models.CASCADE,
                             related_name='variants', verbose_name=_('item'))
    attributes = models.ManyToManyField('ItemAttribute', blank=False,
                                        verbose_name=_('attributes'))
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2,
                                verbose_name=_('price'))
    acquired_by = models.ManyToManyField(
        to='User', blank=True, related_name='item_variants',
        verbose_name=_('acquired by')
    )
    recurrence = models.CharField(max_length=10, choices=INTERVALS,
                                  blank=True, null=True, default=None)

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
        return f'ItemVariant(item=\'{self.item.name}\')'

    def __str__(self):
        return self.name

    def get_attributes_set(self):
        return ', '.join([
            f'{attribute.attribute.name}: {attribute.value}'
            for attribute in self.attributes.all()
        ])

    def get_variant_name(self):
        return f'{self.item.name} ({self.get_attributes_set()})'

    def save(self, *args, **kwargs):
        if self.recurrence is not None and not self.item.is_subscription():
            self.recurrence = None
        elif self.recurrence is None and self.item.is_subscription():
            self.recurrence = 'year'
        return super().save(*args, **kwargs)

    def get_recurrence(self):
        return str(self.recurrence)
