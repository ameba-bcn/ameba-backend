from django.db.models import TextField
from django.contrib.auth.models import Group
from django.db import models

from api.models import Item


class Subscription(Item):
    benefits = TextField(max_length=1000, default='')
    group = models.ForeignKey(Group, blank=True, null=True,
                              on_delete=models.SET_NULL)
