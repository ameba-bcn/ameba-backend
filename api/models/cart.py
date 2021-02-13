import uuid

from django.db.models import (
    Model, ForeignKey, ManyToManyField, JSONField, OneToOneField,
    UUIDField, DateTimeField, SET_NULL, CASCADE
)

from api.stripe import get_create_update_payment_intent
from api.exceptions import CartIsEmpty


class CartItems(Model):
    item = ForeignKey(to='Item', on_delete=CASCADE)
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
    user = OneToOneField(to='User', on_delete=CASCADE, blank=True, null=True)
    items = ManyToManyField(to='Item', through='CartItems')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    discount_code = ForeignKey(to='DiscountCode', on_delete=SET_NULL,
                               blank=True, null=True)
    checkout_details = JSONField(blank=True, null=True)

    def delete(self, using=None, keep_parents=False):
        self.items.clear()
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
            amount += cart_item['item'].amount * fraction
        return int(amount)

    @property
    def cart_items(self):
        return self.get_cart_items_with_discounts()

    def get_cart_items_with_discounts(self):
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
            valid_dis = item.get_valid_discounts(self.user, self.discount_code)
            return sorted(valid_dis, key=lambda x: x.value, reverse=True)
        return []

    def cart_items_by_price_desc(self):
        queryset = self.get_cart_items()
        return sorted(queryset, key=lambda x: x.item.price, reverse=True)

    def get_cart_items(self):
        return self.items.through.objects.filter(cart=self)

    def is_empty(self):
        return not self.get_cart_items().exists()

    def checkout(self):
        if self.is_empty():
            raise CartIsEmpty

        payment_intent = get_create_update_payment_intent(
            amount=self.amount,
            idempotency_key=self.id,
            checkout_details=self.checkout_details
        )
        self.checkout_details = {
            "payment_intent": payment_intent
        }
        self.save()
