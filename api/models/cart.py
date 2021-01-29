import time
import uuid

from django.db.models import (
    Model, ForeignKey, ManyToManyField, CharField, OneToOneField,
    UUIDField, DateTimeField, SET_NULL, CASCADE
)


class CartItems(Model):
    item = ForeignKey(to='Item', on_delete=CASCADE)
    cart = ForeignKey(to='Cart', on_delete=CASCADE)

    @property
    def discount(self):
        if discount := list(filter(
            lambda x: x['cart_item'] == self, self.cart.compute_discounts()
        )):
            return discount[0]['discount']
        return 0


class Cart(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = OneToOneField(to='User', on_delete=CASCADE, blank=True,null=True)
    items = ManyToManyField(to='Item', through='CartItems')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    discount_code = ForeignKey(to='DiscountCode', on_delete=SET_NULL)

    def delete(self, using=None, keep_parents=False):
        self.items.clear()
        return super().delete(using, keep_parents)

    @property
    def total(self):
        return self.get_total()

    def get_total(self, code=None):
        total = 0
        for cart_item in self.compute_discounts(code=code):
            if discount := cart_item['discount']:
                fraction = 1 - discount.value / 100.
            else:
                fraction = 1.
            total += float(cart_item['item'].price) * fraction
        return f'{total} €'

    @property
    def cart_items(self):
        return self.compute_discounts()

    def get_cart_items(self, code=None):
        return self.compute_discounts(code=code)

    def compute_discounts(self, code=None):
        cart_discounts = []
        discounts = []
        cart_items_by_price = self.cart_items_by_price_desc()
        for cart_item in cart_items_by_price:
            discounts_by_value = self.discounts_by_value_desc(
                cart_item.item, code)
            for discount in discounts_by_value:
                if self.is_applicable(cart_discounts, discount):
                    discounts.append({
                        'item': cart_item.item,
                        'discount': discount,
                        'cart_item': cart_item
                    })
                    cart_discounts.append(discount)
                    break
            else:
                discounts.append({
                    'item': cart_item.item,
                    'discount': None,
                    'cart_item': cart_item
                })
        return discounts

    def is_applicable(self, cur_discounts, discount):
        user = self.user
        return discount.remaining_usages(user) > cur_discounts.count(discount)

    def discounts_by_value_desc(self, item, code=None):
        if self.user:
            valid_dis = item.get_valid_discounts(self.user, code)
            return sorted(valid_dis, key=lambda x: x.value, reverse=True)
        return []

    def cart_items_by_price_desc(self):
        queryset = self.get_cart_items()
        return sorted(queryset, key=lambda x: x.item.price, reverse=True)

    def get_cart_items(self):
        return self.items.through.objects.filter(cart=self)
