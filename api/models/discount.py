import random
import string

from datetime import date, timedelta
from django.db import models


MAX_CODE_GEN_RETRIES = 10
FOREVER = -1


class DiscountUsage(models.Model):
    user = models.ForeignKey('User', on_delete=models.DO_NOTHING)
    discount = models.ForeignKey('Discount', on_delete=models.DO_NOTHING)
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
        return self.number_of_uses - self.usages.filter(id=user.id).count()

    @staticmethod
    def _user_match_code(user, code):
        if code and DiscountCode.objects.filter(code=code).exists():
            code_obj = DiscountCode.objects.get(code=code)
            return code_obj.validate_user(user)
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
    code = models.CharField(max_length=6, unique=True)
    user = models.ForeignKey(to='User', on_delete=models.DO_NOTHING,
                             blank=True)
    discount = models.ForeignKey(to='Discount',
                                 on_delete=models.DO_NOTHING,
                                 related_name='user_discounts')
    created = models.DateField(auto_now_add=True)
    days_period = models.IntegerField(default=30, blank=True)
    is_expired = models.BooleanField(default=False)

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

    def get_unique_random_code(self):
        for _ in range(MAX_CODE_GEN_RETRIES):
            code = self._get_random_code()
            if not self.objects.filter(code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if self.pk is None and self.code is None:
            self.code = self.get_unique_random_code()
        return super().save(*args, **kwargs)

    def validate_user(self, user):
        return not self.get_is_expired() and self._is_user_eligible(user)

    def _is_user_eligible(self, user):
        return not self.is_personal or self.user == user

    def _get_random_code(self):
        length = self._meta.get_field('code').max_length
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(length))
