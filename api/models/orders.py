from django.utils.translation import gettext as _
from django.db import models
from django.conf import settings

from api.signals.emails import new_order, order_ready


class Order(models.Model):

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             verbose_name=_('user'), null=True)
    item_variants = models.ManyToManyField(to='ItemVariant', blank=False)
    address = models.CharField(max_length=1000, default=settings.ORDERS_ADDRESS)
    ready = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def send_new_order_notification(self):
        new_order.send(self.__class__, self)

    def send_order_ready_notification(self):


