from django.utils.translation import gettext as _
from django.db import models
from django.db.models import UUIDField

import api.stripe as stripe_api


FP_STATUS = 'paid'
FP_AMOUNT = 0


class PaymentManager(models.Manager):

    @staticmethod
    def create_payment(cart, invoice):
        from api.serializers.cart import CartSerializer
        user = cart.user
        cart_record = CartSerializer(instance=cart).data
        payment = Payment.objects.create(
            cart=cart,
            user=user,
            cart_record=cart_record,
            invoice=invoice,
            invoice_id=invoice['id']
        )
        return payment

    def get_or_create_payment(self, cart, invoice):
        if cart.payment:
            return cart.payment
        else:
            return self.create_payment(cart, invoice)


class Payment(models.Model):
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    id = UUIDField(primary_key=True, editable=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             verbose_name=_('user'))
    cart = models.OneToOneField('Cart', on_delete=models.PROTECT, null=True,
                                related_name='payment')
    cart_record = models.JSONField(verbose_name=_('cart record'))
    invoice = models.JSONField(verbose_name=_('invoice'), blank=False)
    invoice_id = models.CharField(max_length=64, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = PaymentManager()

    @property
    def amount(self):
        return self.invoice and self.invoice['amount_due'] or FP_AMOUNT

    @property
    def status(self):
        if self.invoice is not None:
            return self.invoice['status']
        elif self.amount == 0:
            return FP_STATUS

    @property
    def total(self):
        return "{:.2f} €".format(self.amount/100.)

    def __str__(self):
        return f"Payment(" \
                    f"user='{self.user}', " \
                    f"total='{self.total}', " \
                    f"status'={self.status}" \
               f")"

    def finish_payment(self):
        self.invoice = dict(stripe_api.get_invoice(self.invoice_id))
        if self.status == 'paid':
            cart = self.cart
            self.cart = None
            self.save()
            cart.resolve()
            return True
        return False
