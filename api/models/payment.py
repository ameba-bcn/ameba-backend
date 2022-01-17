import uuid

from django.utils.translation import gettext as _
from django.db import models
from django.db.models import UUIDField
import api.stripe as stripe_api

from api.signals.emails import payment_closed
import api.signals.items as items_signals

FP_STATUS = 'paid'
FP_AMOUNT = 0


class PaymentManager(models.Manager):

    @staticmethod
    def create_payment(user=None, cart=None, invoice=None):
        from api.serializers.cart import CartSerializer
        user = cart.user if hasattr(cart, 'user') and cart.user else user
        payment_attrs = dict(
            cart=cart,
            user=user,
            cart_record=CartSerializer(instance=cart).data if cart else None,
            invoice_id=invoice['id'] if invoice else None,
            payment_intent_id=invoice['payment_intent'] if invoice else None
        )
        if cart:
            payment_attrs['id'] = cart.id
        payment = Payment.objects.create(**payment_attrs)

        if cart:
            for cart_item in cart.get_cart_items():
                payment.item_variants.add(cart_item.item_variant)

        if payment.close():
            payment.refresh_from_db()

        return payment


class Payment(models.Model):
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    id = UUIDField(primary_key=True, editable=True, default=uuid.uuid4)
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             verbose_name=_('user'), null=True)
    cart = models.OneToOneField('Cart', on_delete=models.PROTECT, null=True,
                                related_name='payment')
    cart_record = models.JSONField(verbose_name=_('cart record'), null=True)
    details = models.JSONField(verbose_name=_('invoice'), null=True)
    invoice_id = models.CharField(max_length=128, null=True)
    payment_intent_id = models.CharField(max_length=128, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    item_variants = models.ManyToManyField(
        to='ItemVariant', related_name='payments', blank=False
    )
    objects = PaymentManager()

    @property
    def amount(self):
        """ Returns value of currency units representing total amount to be
        paid.
        :return: Integer
        """
        return self.invoice and self.invoice['amount_due'] or FP_AMOUNT

    @property
    def status(self):
        """ Returns status of the payment. It can be paid in case no payment
        needed or payment already done. In case there's stripe's invoice,
        state matches the invoice state. In case amount > 0 and no invoice
        is attached to this payment, False is returned which means error.
        :return:
        """
        if self.invoice is not None:
            return self.invoice['status']
        elif self.amount == 0:
            return FP_STATUS
        return False

    def closed(self):
        """ Returns whether the payment is closed and item variants attached to
        its user.
        :return: True/False
        """
        return not bool(self.item_variants.all())

    @property
    def cart_hash(self):
        """ Returns hash of products to be purchased.
        :return:
        """
        return str(hash(tuple(
            (iv.id, iv.price) for iv in self.item_variants.all().order_by('id')
        ) + (self.amount, )))

    @property
    def total(self):
        return "{:.2f} €".format(self.amount/100.)

    def __str__(self):
        return f"Payment(" \
                    f"user='{self.user}', " \
                    f"total='{self.total}', " \
                    f"status'={self.status}" \
               f")"

    @property
    def invoice(self):
        """ Stripe's invoice.
        :return: invoice or None
        """
        if self.invoice_id:
            return stripe_api.get_invoice(self.invoice_id)

    @property
    def payment_intent(self):
        """ Stripe's payment intent.
        :return: payment_intent or None
        """
        if self.payment_intent_id:
            return stripe_api.get_payment_intent(self.payment_intent_id)

    @property
    def client_secret(self):
        """ Retrieve payment_intent's client secret from stripe to be used
        in stripe payment form to properly identify payment.
        :return: client_secret string or None
        """
        if payment_intent := self.payment_intent:
            return payment_intent['client_secret']

    def update_details(self):
        """ Update details for the record: invoice and payment_intent record
        copies are saved here. Any other relevant information to be saved can
        be added here.
        :return:
        """
        if self.invoice:
            self.details = {
                'invoice': dict(self.invoice),
                'payment_intent': dict(self.payment_intent)
            }

    def close(self):
        """ At this point, payment is expected to be done. Otherwise,
        False is returned. In case payment is successful, items are attached
        to the user and notifications sent.
        :return: True/False if the payment was successful or not.
        """
        self.update_details()

        if self.cart:
            self.detach_cart()

        if self.status == 'paid' and not self.processed:
            items_signals.items_acquired.send(sender=self.__class__, payment=self)
            if self.amount > 0:
                payment_closed.send(sender=self.__class__, payment=self)
            self.item_variants.clear()
            self.processed = True
            self.save()
            return True
        return False

    def detach_cart(self):
        """ Cart is detached from payment and deleted.
        :return: None
        """
        cart = self.cart
        self.cart = None
        self.save()
        cart.delete()
