import hashlib
import time

from django.db.models import (
    DO_NOTHING, Model, ForeignKey, ManyToManyField, CharField, OneToOneField
)


def _create_hash():
    """ This function generate 10 character long hash
    :return: str
    """
    hsh = hashlib.sha1()
    hsh.update(str(time.time()).encode('utf-8'))
    return hsh.hexdigest()[:20]


class CartItems(Model):
    item = ForeignKey(to='Item', on_delete=DO_NOTHING)
    cart = ForeignKey(to='Cart', on_delete=DO_NOTHING)

    @property
    def discount(self):
        if discount := list(filter(
            lambda x: x['cart_item'] == self, self.cart.compute_discounts()
        )):
            return discount[0]['discount']
        return 0


class Cart(Model):
    hash = CharField(max_length=20, default=_create_hash, unique=True)
    user = OneToOneField(to='User', on_delete=DO_NOTHING, blank=True,null=True)
    items = ManyToManyField(to='Item', through='CartItems')

    @property
    def total(self):
        total = 0
        for cart_item in self.cart_items:
            if discount := cart_item['discount']:
                fraction = 1 - discount.value / 100.
            else:
                fraction = 1.
            total += float(cart_item['item'].price) * fraction
        return f'{total} €'

    @property
    def cart_items(self):
        return self.compute_discounts()

    def compute_discounts(self):
        cart_discounts = []
        discounts = []
        cart_items_by_price = self.cart_items_by_price_desc()
        for cart_item in cart_items_by_price:
            discounts_by_value = self.discounts_by_value_desc(cart_item.item)
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

    def discounts_by_value_desc(self, item):
        if self.user:
            valid_dis = item.get_valid_discounts(self.user)
            return sorted(valid_dis, key=lambda x: x.value, reverse=True)
        return []

    def cart_items_by_price_desc(self):
        queryset = self.get_cart_items()
        return sorted(queryset, key=lambda x: x.item.price, reverse=True)

    def get_cart_items(self):
        return self.items.through.objects.filter(cart=self)
