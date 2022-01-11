import uuid

from django.utils.translation import gettext_lazy as _
from django import dispatch
from django.db.models import (
    Model, ForeignKey, ManyToManyField, JSONField, OneToOneField,
    UUIDField, DateTimeField, SET_NULL, CASCADE, CharField
)
from django.conf import settings

from api.exceptions import (
    CartIsEmpty, CartCheckoutNeedsUser, CartHasMultipleSubscriptions,
    MemberProfileRequired, UserCanNotAcquireTwoIdenticalEvents
)
from api.stripe import IntentStatus
import api.signals.items as items


SUCCEEDED_PAYMENTS = [IntentStatus.SUCCESS, IntentStatus.NOT_NEEDED]


class CartItems(Model):
    class Meta:
        verbose_name = _('Cart items')
        verbose_name_plural = _('Cart items')

    item_variant = ForeignKey(
        to='ItemVariant', on_delete=CASCADE, verbose_name=_('item variant')
    )
    cart = ForeignKey(to='Cart', on_delete=CASCADE, verbose_name=_('cart'))

    @property
    def discount(self):
        if discount := list(filter(
            lambda x: x['cart_item'] == self, self.cart.get_cart_items_with_discounts()
        )):
            return discount[0]['discount']
        return 0


class Cart(Model):
    class Meta:
        verbose_name = _('cart')

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = OneToOneField(to='User', on_delete=CASCADE, blank=True,
                         null=True, related_name='_cart', verbose_name='user')
    item_variants = ManyToManyField(
        to='ItemVariant', through='CartItems', verbose_name=_('item variants')
    )
    created = DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = DateTimeField(auto_now=True, verbose_name=_('updated'))
    discount_code = ForeignKey(
        to='DiscountCode', on_delete=SET_NULL, blank=True, null=True,
        verbose_name=_('discount code')
    )
    checkout_details = JSONField(
        blank=True, null=True, verbose_name=_('checkout details')
    )
    checkout_hash = CharField(
        blank=True, max_length=128, verbose_name=_('checkout hash')
    )

    def delete(self, using=None, keep_parents=False):
        self.item_variants.clear()
        return super().delete(using, keep_parents)

    @property
    def total(self):
        return '{:.2f} €'.format(self.amount / 100.)

    def get_hash(self):
        return str(hash(tuple(
            (iv.id, iv.price) for iv in self.item_variants.all().order_by('id')
        ) + (self.amount, )))

    @property
    def amount(self):
        amount = 0
        for cart_item in self.get_cart_items_with_discounts():
            if discount := cart_item['discount']:
                fraction = 1. - discount.value / 100.
            else:
                fraction = 1.
            amount += cart_item['item_variant'].amount * fraction
        return int(amount)

    @property
    def computed_item_variants(self):
        return self.get_cart_items_with_discounts()

    def get_cart_items_with_discounts(self):
        cart_discounts = []
        discounts = []
        cart_items_by_price = self.cart_items_by_price_desc()
        for cart_item in cart_items_by_price:
            discounts_by_value = self.discounts_by_value_desc(cart_item.item_variant)
            for discount in discounts_by_value:
                if self.is_applicable(cart_discounts, discount):
                    discounts.append({
                        'item_variant': cart_item.item_variant,
                        'discount': discount,
                        'cart_item': cart_item
                    })
                    cart_discounts.append(discount)
                    break
            else:
                discounts.append({
                    'item_variant': cart_item.item_variant,
                    'discount': None,
                    'cart_item': cart_item
                })
        return discounts

    def is_applicable(self, cur_discounts, discount):
        user = self.user
        return discount.remaining_usages(user) > cur_discounts.count(discount)

    def discounts_by_value_desc(self, item_variant):
        if self.user:
            valid_dis = item_variant.item.get_valid_discounts(
                self.user, self.discount_code
            )
            return sorted(valid_dis, key=lambda x: x.value, reverse=True)
        return []

    def cart_items_by_price_desc(self):
        queryset = self.get_cart_items()
        return sorted(queryset, key=lambda x: x.item_variant.price, reverse=True)

    def get_cart_items(self):
        """ Return cart_items objects which relates item_variants with
        carts."""
        return self.item_variants.through.objects.filter(cart=self)

    def is_empty(self):
        return not self.get_cart_items().exists()

    def is_anonymous(self):
        return not self.user

    @property
    def subscriptions(self):
        return [
            x.item.subscription for x in self.item_variants.all() if
            x.item.is_subscription()
        ]

    @property
    def subscription(self):
        if len(self.subscriptions) == 1:
            return self.subscriptions[0]
        return None

    @property
    def events(self):
        return [
            x.item.event for x in self.item_variants.all() if
            x.item.is_event()
        ]

    @property
    def articles(self):
        return [
            x.item.subscription for x in self.item_variants.all() if
            x.item.is_article()
        ]

    def has_multiple_subscriptions(self):
        return len(self.subscriptions) > 1

    def has_identical_events(self):
        current_events = []
        for event in self.events:
            if event.id in current_events:
                return True
            if self.user and event.acquired_by.filter(pk=self.user.pk):
                return True
            current_events.append(event.id)
        return False

    def has_changed(self):
        if self.checkout_hash != self.get_hash():
            self.save()
            return True
        return False

    def is_checkout_able(self):
        if self.is_empty():
            raise CartIsEmpty
        if self.is_anonymous():
            raise CartCheckoutNeedsUser
        if self.has_multiple_subscriptions():
            raise CartHasMultipleSubscriptions
        if self.has_identical_events():
            raise UserCanNotAcquireTwoIdenticalEvents
        if self.subscription and not self.user.has_member_profile():
            raise MemberProfileRequired

    def checkout(self):
        self.is_checkout_able()
        self.checkout_hash = self.get_hash()
        self.save()

    def set_checkout_details(self, checkout_details):
        self.checkout_details = checkout_details
        self.save()

    def has_user(self):
        return self.user and True or False

    def has_member_profile(self):
        if self.has_user():
            return self.user.has_member_profile()
        return False

    def has_memberships(self):
        if self.has_user() and self.has_member_profile():
            return len(self.user.member.memberships.all()) > 0
        return False

    @property
    def state(self):
        return dict(
            has_user=self.has_user(),
            has_member_profile=self.has_member_profile(),
            has_memberships=self.has_memberships(),
            has_articles=len(self.articles),
            has_events=len(self.events),
            has_subscriptions=len(self.subscriptions),
            needs_checkout=self.has_changed()
        )

    def is_payment_succeeded(self):
        if not self.checkout_details:
            return False
        elif 'payment_intent' not in self.checkout_details:
            return False
        elif self.checkout_details['payment_intent']['status']\
          not in SUCCEEDED_PAYMENTS and not settings.DEBUG:
            return False
        return True

    def resolve(self):
        """ Directly process cart items without passing through payment. """
        items.items_acquired.send(self.__class__, self)
        return super().delete()
