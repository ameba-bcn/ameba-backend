import uuid

from django.db.models import (
    Model, ForeignKey, ManyToManyField, JSONField, OneToOneField,
    UUIDField, DateTimeField, SET_NULL, CASCADE
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

    def delete(self, using=None, keep_parents=False):
        self.item_variants.clear()
        return super().delete(using, keep_parents)

    @property
    def total(self):
        return '{:.2f} €'.format(self.amount / 100.)

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
    def cart_items(self):
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
