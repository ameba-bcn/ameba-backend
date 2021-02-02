import random
import string
import hashlib
import datetime

from datetime import date, timedelta
from django.db import models


MAX_CODE_GEN_RETRIES = 1000
FOREVER = -1


def get_random_code():
    return hashlib.sha1(
        str(datetime.datetime.now()).encode('UTF-8')
    ).hexdigest().upper()[:6]


class DiscountUsage(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    discount = models.ForeignKey('Discount', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class Discount(models.Model):
    name = models.CharField(max_length=25)
    value = models.IntegerField(verbose_name='Value (%)')
    items = models.ManyToManyField(to='Item', related_name='discounts')
    groups = models.ManyToManyField(to='auth.Group')
    need_code = models.BooleanField()
    number_of_uses = models.IntegerField()
    usages = models.ManyToManyField(
        to='User',
        through='DiscountUsage',
        related_name='used_discounts'
    )

    def __str__(self):
        return f'{self.name} ({self.value}%)'

    def check_user_applies(self, user, code=None):
        if not self.need_code or self._user_match_code(user, code):
            if self._user_match_groups(user) and self._user_match_usages(user):
                return True
        return False

    def remaining_usages(self, user):
        if self.number_of_uses == -1:
            return 9999
        return self.number_of_uses - self.usages.filter(id=user.id).count()

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
    code = models.CharField(max_length=6, default=get_random_code,
                            primary_key=True)
    user = models.ForeignKey(to='User', on_delete=models.CASCADE,
                             blank=True)
    discount = models.ForeignKey(to='Discount',
                                 on_delete=models.CASCADE,
                                 related_name='user_discounts')
    created = models.DateField(auto_now_add=True)
    days_period = models.IntegerField(default=30, blank=True)
    is_expired = models.BooleanField(default=False)

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
