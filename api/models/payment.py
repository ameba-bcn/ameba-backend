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
    def create_payment(cart, invoice):
        from api.serializers.cart import CartSerializer
        user = cart.user
        cart_record = CartSerializer(instance=cart).data

        if invoice['id'] != stripe_api.EMPTY_INVOICE_ID:
            payment_intent = stripe_api.get_payment_intent(
                invoice['payment_intent_id']
            )
        else:
            payment_intent = stripe_api.EMPTY_PAYMENT_INTENT

        payment = Payment.objects.create(
            id=cart.id,
            cart=cart,
            user=user,
            cart_record=cart_record,
            invoice=invoice,
            cart_hash=cart.checkout_hash,
            invoice_id=invoice['id'],
            payment_intent_id=payment_intent['id']
        )

        for cart_item in cart.get_cart_items():
            payment.item_variants.add(cart_item.item_variant)

        return payment

    def get_or_create_payment(self, cart, invoice):
        if hasattr(cart, 'payment') and cart.payment is not None:
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
    cart_hash = models.CharField(blank=True, max_length=128,
                                 verbose_name=_('cart checkout hash'))
    details = models.JSONField(verbose_name=_('invoice'), null=True)
    invoice_id = models.CharField(max_length=128, null=True)
    payment_intent_id = models.CharField(max_length=128, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
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
        self.details = {
            'invoice': dict(self.invoice),
            'payment_intent': dict(self.payment_intent)
        }

    def close_payment(self):
        """ At this point, payment is expected to be done. Otherwise,
        False is returned. In case payment is successful, items are attached
        to the user and notifications sent.
        :return: True/False if the payment was successful or not.
        """
        self.update_details()
        if self.status == 'paid':
            items_signals.items_acquired.send(sender=self.__class__, payment=self)
            if self.amount > 0:
                payment_closed.send(sender=self.__class__, payment=self)
            if self.cart:
                self.detach_cart()
            self.item_variants.clear()
            return True
        return False

    def detach_cart(self):
        """ Cart is detached from payment and deleted.
        :return: None
        """
        cart = self.cart
        self.cart = None
        cart.delete()
        self.save()
