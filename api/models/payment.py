from django.utils.translation import gettext as _
from django.db import models
from django.db.models import UUIDField

from api import stripe


class PaymentManager(models.Manager):

    @staticmethod
    def create_payment(cart, payment_intent):
        from api.serializers.cart import CartSerializer
        user = cart.user
        cart_record = CartSerializer(instance=cart).data
        payment = Payment.objects.create(
            id=cart.id,
            user=user,
            cart_record=cart_record,
            details=dict(payment_intent)
        )
        return payment


class Payment(models.Model):
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    id = UUIDField(primary_key=True, editable=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             verbose_name=_('user'))
    cart_record = models.JSONField(verbose_name=_('cart record'))
    details = models.JSONField(verbose_name=_('details'))
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PaymentManager()

    @property
    def amount(self):
        return self.details['amount']

    @property
    def status(self):
        return self.details['status']

    @property
    def total(self):
        return "{:.2f} €".format(self.amount/100.)

    def __str__(self):
        return f"Payment(" \
                    f"user='{self.user}', " \
                    f"total='{self.total}', " \
                    f"status'={self.status}" \
               f")"
