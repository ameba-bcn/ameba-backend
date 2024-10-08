from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum
from django.db import models
from django.utils.translation import gettext as _
import api.cache_utils as cache_utils

EXPIRE_HOURS_BEFORE_EVENT = 1
EXPIRE_BEFORE_EVENT = timedelta(hours=EXPIRE_HOURS_BEFORE_EVENT)


INTERVALS = [(i, i) for i in settings.SUBSCRIPTION_RECURRENCES.split(',')]

PERIODS = {
    'year': 365,
    'day': 1,
    'month': 30,
    'week': 7
}


if settings.DEBUG:
    INTERVALS.append(('day', 'day'))

INTERVALS = tuple(INTERVALS)


item_stock_hint = _(
    'Usa este campo para indicar la cantidad de stock disponible.\n'
    'Si se trata de un evento, introduce el número de plazas/entradas disponibles.\n'
    'Si la gestión del aforo no se realiza a través de la web, introduce -1.\n'
    'Por ejemplo, si la entrada es libre hasta completar aforo o si la venta de entradas se gestiona directamente en taquilla.'
)

item_price_hint = _(
    'Usa este campo para indicar el precio del producto o evento.'
    'Si es un evento gratuito, introduce el valor 0.'
)


class Item(models.Model):
    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    name = models.CharField(
        max_length=100, unique=True, verbose_name=_('name')
    )
    description = models.TextField(
        max_length=5000, verbose_name=_('description')
    )
    images = models.ManyToManyField(
        to='Image', blank=False, verbose_name=_('images')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    order = models.DateTimeField(verbose_name=_('order'), default=timezone.now)
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

    @property
    def price(self):
        prices = list(variant.price for variant in self.variants.all())
        if prices:
            return min(prices)

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

    def get_type(self):
        if self.is_subscription():
            return 'subscription'
        elif self.is_article():
            return 'article'
        elif self.is_event():
            return 'event'
        else:
            return 'item'

    @cache_utils.invalidate_models_cache
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class ItemAttributeType(models.Model):
    class Meta:
        verbose_name = _('Item attribute type')
        verbose_name_plural = _('Item attribute types')

    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name

    @cache_utils.invalidate_models_cache
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


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

    @cache_utils.invalidate_models_cache
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class ItemVariant(models.Model):
    class Meta:
        verbose_name = _('Item variant')
        verbose_name_plural = _('Item variants')

    item = models.ForeignKey('Item', on_delete=models.CASCADE,
                             related_name='variants', verbose_name=_('item'))
    attributes = models.ManyToManyField('ItemAttribute', blank=False,
                                        verbose_name=_('attributes'),
                                        related_name='variants')
    stock = models.IntegerField(help_text=item_stock_hint, verbose_name=_('stock'))
    price = models.DecimalField(max_digits=8, decimal_places=2,
                                verbose_name=_('price'), help_text=item_price_hint)
    acquired_by = models.ManyToManyField(
        to='User', blank=True, related_name='item_variants',
        verbose_name=_('acquired by')
    )
    checked_in = models.ManyToManyField(
        to='User', blank=True, related_name='checked_in_events',
        verbose_name=_('checked in')
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
        return self.get_variant_name()

    def __str__(self):
        return self.get_variant_name()

    def get_attributes_set(self):
        return ', '.join([
            f'{attribute.attribute.name}: {attribute.value}'
            for attribute in self.attributes.all()
        ])

    def get_variant_name(self):
        if self.item.is_subscription():
            return f'{self.item.name} Membership'
        return f'{self.item.name} ({self.get_attributes_set()})'

    @cache_utils.invalidate_models_cache
    def save(self, *args, **kwargs):
        if self.recurrence is not None and not self.item.is_subscription():
            self.recurrence = None
        elif self.recurrence is None and self.item.is_subscription():
            self.recurrence = 'year'
        return super().save(*args, **kwargs)

    def get_recurrence(self):
        return self.recurrence and str(self.recurrence) or None

    def is_periodic(self):
        return self.get_recurrence() is not None

    @property
    def period(self):
        return PERIODS.get(self.get_recurrence(), None)

