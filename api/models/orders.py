import uuid

from django.utils.translation import gettext as _
from django.db import models
from django.db.models import UUIDField
import api.stripe as api_stripe

from api.signals.emails import payment_closed
import api.signals.items as items_signals


class Order(models.Model):

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             verbose_name=_('user'), null=True)
    item_variants = models.ManyToManyField(to='ItemVariant', blank=False)
    ready = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def send_new_order_notification(self):
        pass

    def send_order_ready_notification(self):
        pass

