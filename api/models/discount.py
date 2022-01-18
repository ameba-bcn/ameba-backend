import hashlib
import datetime
from datetime import date, timedelta

from django.utils.translation import gettext_lazy as _
from django.db import models
import django.core.validators as validators
import api.stripe as api_stripe


MAX_CODE_GEN_RETRIES = 1000
FOREVER = -1


def get_random_code():
    return hashlib.sha1(
        str(datetime.datetime.now()).encode('UTF-8')
    ).hexdigest().upper()[:6]


class DiscountUsage(models.Model):
    class Meta:
        verbose_name = _('Discount usage')
        verbose_name_plural = _('Discount usages')

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, verbose_name=_('user')
    )
    discount = models.ForeignKey(
        'Discount', on_delete=models.CASCADE, verbose_name=_('discount')
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )


class Discount(models.Model):
    class Meta:
        verbose_name = _('Discount')
        verbose_name_plural = _('Discounts')

    name = models.CharField(max_length=25, verbose_name=_('name'))
    value = models.IntegerField(verbose_name=_('Value (%)'), validators=[
        validators.MaxValueValidator(100), validators.MinValueValidator(0)
    ])
    items = models.ManyToManyField(
        to='Item', related_name='discounts', verbose_name=_('items')
    )
    groups = models.ManyToManyField(to='auth.Group', verbose_name=_('groups'))
    need_code = models.BooleanField(verbose_name=_('need code'))
    usages = models.ManyToManyField(
        to='User',
        through='DiscountUsage',
        related_name='used_discounts',
        verbose_name=_('usages')
    )
    is_single_use = models.BooleanField(default=True)

    @property
    def number_of_uses(self):
        return 1 if self.is_single_use else -1

    def __str__(self):
        return f'{self.name} ({self.value}%)'

    def check_user_applies(self, user, code=None):
        if not self.need_code or self._user_match_code(user, code):
            if self._user_match_groups(user) and self._user_match_usages(user):
                return True
        return False

    def remaining_usages(self, user):
        if not self.is_single_use:
            return 9999
        elif self._already_used_by(user):
            return 0
        return 1

    def _already_used_by(self, user):
        return bool(self.usages.filter(id=user.id))

    @staticmethod
    def _user_match_code(user, code):
        if code:
            return code.validate_user(user)
        return False

    def _user_match_groups(self, user):
        for user_group in user.groups.all():
            if user_group in self.groups.all():
                return True
        return False

    def _user_match_usages(self, user):
        if (
            self.remaining_usages(user) > 0
            or self.remaining_usages(user) == FOREVER
        ):
            return True
        return False


class DiscountCode(models.Model):
    class Meta:
        verbose_name = _('Discount code')
        verbose_name_plural = _('Discount codes')

    code = models.CharField(
        max_length=6, default=get_random_code,
        primary_key=True, verbose_name=_('code'))
    user = models.ForeignKey(to='User', on_delete=models.CASCADE, null=True,
                             blank=True, verbose_name=_('user'))
    discount = models.ForeignKey(to='Discount',
                                 on_delete=models.CASCADE,
                                 related_name='user_discounts',
                                 verbose_name=_('discount'))
    created = models.DateField(auto_now_add=True, verbose_name=_('created'))
    days_period = models.IntegerField(default=30, blank=True,
                                      verbose_name=_('days period'))
    is_expired = models.BooleanField(
        default=False, verbose_name=_('is expired')
    )

    def __str__(self):
        return '{code} ({discount})'.format(code=self.code,
                                            discount=self.discount)

    @property
    def expired(self):
        return self.get_is_expired()

    @property
    def is_personal(self):
        return bool(self.user)

    def expire(self):
        self.is_expired = True
        self.save()

    def get_is_expired(self):
        if date.today() >= self.created + timedelta(days=self.days_period):
            self.expire()
        return self.is_expired

    def validate_user(self, user):
        return not self.get_is_expired() and self._is_user_eligible(user)

    def _is_user_eligible(self, user):
        return not self.is_personal or self.user == user
