import uuid

from django.db.models import (
    Model, ForeignKey, ManyToManyField, JSONField, OneToOneField,
    UUIDField, DateTimeField, SET_NULL, CASCADE, CharField
)


CART_STATES = (
    ('checkout_failed', 'checkout_failed'),
    ('payment_pending', 'payment_pending'),
    ('payment_failed', 'payment_failed')
)


class CartItems(Model):
    item_variant = ForeignKey(to='ItemVariant', on_delete=CASCADE)
    cart = ForeignKey(to='Cart', on_delete=CASCADE)

    @property
    def discount(self):
        if discount := list(filter(
            lambda x: x['cart_item'] == self, self.cart.get_cart_items_with_discounts()
        )):
            return discount[0]['discount']
        return 0


class Cart(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = OneToOneField(to='User', on_delete=CASCADE, blank=True,
                         null=True, related_name='_cart')
    item_variants = ManyToManyField(to='ItemVariant', through='CartItems')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    discount_code = ForeignKey(to='DiscountCode', on_delete=SET_NULL,
                               blank=True, null=True)
    checkout_details = JSONField(blank=True, null=True)
    checkout_hash = CharField(blank=True, max_length=128)
    state = CharField(max_length=20, blank=True, choices=CART_STATES)

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

    def has_multiple_subscriptions(self):
        return len(self.subscriptions) > 1

    def has_changed(self):
        return self.checkout_hash != self.get_hash()

    def checkout(self, checkout_details):
        self.checkout_details = checkout_details
        self.checkout_hash = self.get_hash()
        self.save()
