from django.db import models


class Discount(models.Model):
    value = models.IntegerField()
    articles = models.ManyToManyField(to='Item', related_name='discounts')
