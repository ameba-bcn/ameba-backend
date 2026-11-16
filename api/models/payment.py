import datetime
import logging
import uuid

from django.utils import timezone
from django.utils.translation import gettext as _
from django.db import models
from django.db.models import UUIDField
import api.email_factories as email_factories
import api.stripe as api_stripe

from api.signals.emails import payment_closed
from api.signals.items import item_acquired

FP_STATUS = 'paid'
FP_AMOUNT = 0

logger = logging.getLogger(__name__)


class PaymentManager(models.Manager):

    @staticmethod
    def create_payment(user=None, cart=None, invoice=None, item_variants=None,
                       fingerprint=None):
        from api.serializers.cart import CartSerializer
        user = cart.user if hasattr(cart, 'user') and cart.user else user

        details = {}
        if invoice:
            details['invoice'] = dict(invoice)
            if invoice['payment_intent']:
                details['payment_intent'] = dict(
                    api_stripe.get_payment_intent(invoice['payment_intent'])
                )
            invoice_id = invoice['id']
        else:
            invoice_id = None
        if fingerprint:
            # Hash of what was in the cart when this invoice was created:
            # lets the payment endpoint reuse it while the cart is unchanged
            details['cart_fingerprint'] = fingerprint

        payment_attrs = dict(
            cart=cart,
            user=user,
            cart_record=CartSerializer(instance=cart).data if cart else None,
            invoice_id=invoice_id,
            details=details or None
        )
        # Historically Payment.id == Cart.id. Keep it for the first payment
        # of a cart; a cart whose previous invoice was discarded (contents
        # changed) gets a fresh id for the new one.
        if cart and not Payment.objects.filter(id=cart.id).exists():
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
    # SET_NULL: the cart now lives until the payment succeeds, so it can be
    # deleted while a payment is pending (e.g. replaced on login, user
    # deleted); the payment keeps its cart_record snapshot.
    cart = models.OneToOneField('Cart', on_delete=models.SET_NULL, null=True,
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
        False is returned and nothing changes (the cart is kept, so the
        customer can retry the same PaymentIntent or change the cart). In case
        payment is successful, the cart is consumed, items are attached to the
        user and notifications sent.

        Callers that can race (webhook, payment endpoint) must hold a
        select_for_update lock on this payment (see
        api.stripe.fulfil_invoice_payment) so it is processed only once.
        :return: True/False if the payment was successful or not.
        """
        self.update_details()

        if self.status != 'paid' or self.processed:
            return False

        if self.cart:
            self.detach_cart()

        # Emails are sent only once the fulfilment is committed, and a mail
        # provider failure is logged instead of failing (and rolling back)
        # the fulfilment.
        with email_factories.send_after_commit():
            delivery_kwargs = self._get_delivery_kwargs()
            membership_starts = self._get_renewal_period_start()
            if membership_starts is not None:
                delivery_kwargs['membership_starts'] = membership_starts
            for item_variant in self.item_variants.all():
                item_variant.acquired_by.add(self.user)
                item_acquired.send(
                    sender=self.__class__,
                    user=self.user,
                    item_variant=item_variant,
                    **delivery_kwargs
                )

            if self.amount > 0:
                self._set_payment_method_default()
                payment_closed.send(sender=self.__class__, payment=self)
        self.item_variants.clear()
        self.processed = True
        self.save()
        logger.info('Payment %s fulfilled (invoice %s, user %s)', self.id,
                    self.invoice_id, self.user_id)
        return True

    def _get_renewal_period_start(self):
        """ For a membership renewal (invoice generated by Stripe at the end
        of the billing period) paid late, e.g. by a Smart Retry days later,
        returns the start of the period Stripe charged for. None otherwise.
        """
        invoice = self.invoice or {}
        if invoice.get('billing_reason') != 'subscription_cycle':
            return None
        lines = (invoice.get('lines') or {}).get('data') or []
        for line in lines:
            period_start = (line.get('period') or {}).get('start')
            if line.get('type') == 'subscription' and period_start:
                starts = datetime.datetime.fromtimestamp(
                    period_start, tz=datetime.timezone.utc
                )
                return starts if starts < timezone.now() else None
        return None

    def _set_payment_method_default(self):
        """ Memberships only: the card used becomes the customer's default
        for the renewals. One-off purchases don't save the card
        (no setup_future_usage), so there's nothing to set as default.
        """
        invoice = self.invoice or {}
        if not invoice.get('subscription'):
            return
        try:
            api_stripe.set_payment_method_default(self.payment_intent)
        except Exception:
            logger.exception('Could not set default payment method for '
                             'payment %s', self.id)

    def refresh_cart_record(self):
        """ Re-snapshot the cart (delivery details may have been edited
        after the invoice was created) while it is still attached. """
        from api.serializers.cart import CartSerializer
        if self.cart:
            self.cart_record = CartSerializer(instance=self.cart).data
            self.save(update_fields=['cart_record'])

    def _get_delivery_kwargs(self):
        """ Cart is already deleted (see detach_cart, called before this)
        by the time item_variants are being handed out, so delivery info is
        read from cart_record, the JSON snapshot of the cart taken at
        payment creation time (see PaymentManager.create_payment).
        :return: dict of delivery-related fields to attach to Orders.
        """
        fields = [
            'delivery_method', 'pickup_location', 'shipping_name',
            'shipping_address', 'shipping_postal_code', 'shipping_city'
        ]
        record = self.cart_record or {}
        return {field: record.get(field, '') for field in fields}

    def detach_cart(self, delete=True):
        """ Cart is detached from payment and (by default) deleted. Called
        with delete=False when this payment is discarded but the cart lives on
        (its contents changed and a new payment will be created for it).
        :return: None
        """
        cart = self.cart
        self.cart = None
        self.save()
        if delete and cart is not None:
            cart.delete()
