from django.db import models
from django.db.models import Sum


class Item(models.Model):
    name = models.CharField(max_length='25', unique=True)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()

    def get_stock(self):
        if stock := self.variants.aggregate(Sum('stock'))['stock__sum'] > 0:
            return stock
        else:
            return self.stock


class ItemTags(models.Model):
    item = models.ForeignKey(
        to='Item', related_name='tags', on_delete=models.DO_NOTHING
    )
    name = models.CharField('25')


class ItemImage(models.Model):
    item = models.ForeignKey('Item', on_delete=models.DO_NOTHING)
    image = models.ImageField()
    active = models.BooleanField()


class ItemVariant(models.Model):
    category = models.CharField(max_length='25')
    name = models.CharField(max_length='25')
    item = models.ForeignKey(
        to='Item', on_delete=models.DO_NOTHING, related_name='variants'
    )
    stock = models.IntegerField()
    description = models.TextField(max_length=1000, blank=True)

    def get_description(self):
        if self.description:
            return self.description
        else:
            return self.item.description


class ItemVariantImage(models.Model):
    item_variant = models.ForeignKey(
        to='ItemVariant', on_delete=models.DO_NOTHING, related_name='pictures'
    )
    image = models.ImageField()
    active = models.BooleanField()

