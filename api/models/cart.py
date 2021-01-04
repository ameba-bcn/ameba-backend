from django.db import models


class CartItems(models.Model):
    item = models.ForeignKey(to='Item', on_delete=models.DO_NOTHING)
    cart = models.ForeignKey(to='Cart', on_delete=models.DO_NOTHING)
    discount = models.IntegerField()


class Cart(models.Model):
    user = models.ForeignKey(
        to='User', on_delete=models.DO_NOTHING, blank=True, unique=True
    )
    items = models.ManyToManyField(to='CartItems', through=CartItems)

    @property
    def subtotal(self):
        return None

    @property
    def availability(self):
        return None

    def checkout(self):
        pass

    def compute_discounts(self, user):
        pass
