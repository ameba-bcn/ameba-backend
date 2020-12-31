import random
import string

from datetime import date, timedelta
from django.db import models


MAX_CODE_GEN_RETRIES = 10


class Discount(models.Model):
    name = models.CharField(max_length=25)
    value = models.IntegerField()
    items = models.ManyToManyField(to='Item', related_name='discounts')
    groups = models.ManyToManyField(to='auth.Group')
    need_code = models.BooleanField()
    number_of_uses = models.IntegerField()

    def __str__(self):
        return f'{self.name} ({self.value}%)'


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

    def get_random_code(self):
        length = self._meta.get_field('code').max_length
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(length))

    def get_unique_random_code(self):
        for _ in range(MAX_CODE_GEN_RETRIES):
            code = self.get_random_code()
            if not self.objects.filter(code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if self.pk is None and self.code is None:
            self.code = self.get_unique_random_code()
        return super().save(*args, **kwargs)
