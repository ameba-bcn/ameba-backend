from django.db.models import (
    DO_NOTHING, Model, ForeignKey, ManyToManyField, FloatField
)


class CartItems(Model):
    item = ForeignKey(to='Item', on_delete=DO_NOTHING)
    cart = ForeignKey(to='Cart', on_delete=DO_NOTHING)
    discount = ForeignKey(to='Discount', on_delete=DO_NOTHING, blank=True)

    def set_discount(self, discount):
        self.discount = discount
        self.save()


class Cart(Model):
    user = ForeignKey(to='User', on_delete=DO_NOTHING, blank=True, unique=True)
    items = ManyToManyField(to='CartItems', through=CartItems)

    @property
    def total(self):
        total = 0
        for cart_item in self.items.through.all():
            total += cart_item.item.price * (1 - cart_item.discount.value)
        return total

    def get_current_discounts(self):
        return [car_item.discount for car_item in self.items.through.all()]

    def compute_discounts(self):
        cart_discounts = []
        items_by_price = self.items_by_price_desc()
        for cart_item in items_by_price:
            discounts_by_value = self.discounts_by_value_desc(cart_item.item)
            for discount in discounts_by_value:
                if self.is_applicable(cart_discounts, discount):
                    cart_item.set_discount(discount)
                    cart_discounts.append(discount)

    def is_applicable(self, cur_discounts, discount):
        user = self.user
        return discount.remaining_usages(user) > cur_discounts.count(discount)

    def discounts_by_value_desc(self, item):
        valid_dis = item.get_valid_discounts(self.user)
        return sorted(valid_dis, key=lambda x: x.value, reverse=True)

    def items_by_price_desc(self):
        queryset = self.items.through.all()
        return sorted(queryset, key=lambda x: x.item.price, reverse=True)
