from django.utils.translation import gettext as _
from django.db import models
from django.conf import settings

from api.signals.emails import new_order, order_ready


class Order(models.Model):

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             verbose_name=_('user'), null=True)
    item_variants = models.ManyToManyField(to='ItemVariant', blank=False)
    address = models.CharField(
        max_length=1000,
        default=settings.ORDERS_ADDRESS,
        verbose_name=_('address')
    )
    ready = models.BooleanField(default=False, verbose_name=_('ready'))
    delivered = models.BooleanField(default=False, verbose_name=_('delivered'))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.was_ready = self.ready

    def send_new_order_notification(self):
        new_order.send(self.__class__, self)

    def send_order_ready_notification(self):
        order_ready.send(self.__class__, self)

    def save(self, *args, **kwargs):
        if not self.was_ready and self.ready:
            self.send_order_ready_notification()
        return super().save(*args, **kwargs)
