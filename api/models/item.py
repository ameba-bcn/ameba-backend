from django.db import models
from django.db.models import Sum


class Item(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()

    def get_stock(self):
        if stock := self.variants.aggregate(Sum('stock'))['stock__sum'] > 0:
            return stock
        else:
            return self.stock

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(to=Item, on_delete=models.DO_NOTHING,
                             related_name='images')
    image = models.ImageField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.image.name


class ItemVariant(models.Model):
    name = models.CharField(max_length=25)
    item = models.ForeignKey(
        to=Item, on_delete=models.DO_NOTHING, related_name='variants'
    )
    stock = models.IntegerField()
    description = models.TextField(max_length=1000, blank=True)
    image = models.ImageField(blank=True)

    def get_description(self):
        if self.description:
            return self.description
        else:
            return self.item.description

    def __str__(self):
        return self.name
