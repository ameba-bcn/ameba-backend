from django.utils.translation import gettext as _
from django.db.models import TextField
from django.contrib.auth.models import Group
from django.db import models

from api.models import Item


class Subscription(Item):
    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    benefits = TextField(
        max_length=1000, default='', verbose_name=_('benefits')
    )
    group = models.ForeignKey(
        Group, on_delete=models.DO_NOTHING, verbose_name=_('group')
    )
