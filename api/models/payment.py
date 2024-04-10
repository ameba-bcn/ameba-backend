import uuid

from django.utils.translation import gettext as _
from django.db import models
from django.db.models import UUIDField
import api.stripe as api_stripe

from api.signals.emails import payment_closed
from api.signals.items import item_acquired

FP_STATUS = 'paid'
FP_AMOUNT = 0


class PaymentManager(models.Manager):

    @staticmethod
    def create_payment(user=None, cart=None, invoice=None, item_variants=None):
        from api.serializers.cart import CartSerializer
        user = cart.user if hasattr(cart, 'user') and cart.user else user

        if invoice:
            details = {
                'invoice': dict(invoice),
                'payment_intent': dict(
                    api_stripe.get_payment_intent(invoice['payment_intent'])
                )
            }
            invoice_id = invoice['id']
        else:
            details = None
            invoice_id = None

        payment_attrs = dict(
            cart=cart,
            user=user,
            cart_record=CartSerializer(instance=cart).data if cart else None,
            invoice_id=invoice_id,
            details=details
        )
        if cart:
            payment_attrs['id'] = cart.id
        payment = Payment.objects.create(**payment_attrs)
        if cart:
            for cart_item in cart.get_cart_items():
                payment.item_variants.add(cart_item.item_variant)
        elif item_variants:
            payment.item_variants.add(*item_variants)

        if payment.close():
            payment.refresh_from_db()

        return payment


class Payment(models.Model):
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    id = UUIDField(primary_key=True, editable=True, default=uuid.uuid4)
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, verbose_name=_('user'),
        null=True, related_name='payments'
    )
    cart = models.OneToOneField('Cart', on_delete=models.PROTECT, null=True,
                                related_name='payment')
    cart_record = models.JSONField(verbose_name=_('cart record'), null=True)
    details = models.JSONField(verbose_name=_('invoice'), null=True)
    invoice_id = models.CharField(max_length=128, null=True)
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
    def payment_intent(self):
        """ Stripe's payment intent.
        :return: payment_intent or None
        """
        det = self.details
        if det and 'payment_intent' in det and det['payment_intent']:
            return self.details['payment_intent']

    @property
    def payment_intent_id(self):
        if self.payment_intent:
            return self.payment_intent['id']

    @property
    def client_secret(self):
        """ Retrieve payment_intent's client secret from stripe to be used
        in stripe payment form to properly identify payment.
        :return: client_secret string or None
        """
        if payment_intent := self.payment_intent:
            return payment_intent['client_secret']

    @property
    def invoice(self):
        details = self.details
        if details and 'invoice' in details and details['invoice']:
            return self.details['invoice']

    def update_details(self):
        """ Update details for the record: invoice and payment_intent record
        copies are saved here. Any other relevant information to be saved can
        be added here.
        :return:
        """
        if not self.details or 'invoice' not in self.details:
            return
        invoice = api_stripe.find_invoice(self.invoice['id'])
        if not invoice or not invoice['payment_intent']:
            return
        pi = api_stripe.get_payment_intent(invoice['payment_intent'])
        details = self.details if self.details else {}
        details['invoice'] = dict(invoice)
        details['payment_intent'] = dict(pi)
        self.details = details
        self.save()

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
            for item_variant in self.item_variants.all():
                item_variant.acquired_by.add(self.user)
                item_acquired.send(
                    sender=self.__class__,
                    user=self.user,
                    item_variant=item_variant
                )

            if self.amount > 0:
                api_stripe.set_payment_method_default(self.payment_intent)
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
