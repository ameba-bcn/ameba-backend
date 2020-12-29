from django.db import models


class ItemFamily(models.Model):
    name = models.CharField(max_length='25', unique=True)
    description = models.TextField(max_length=1000)

    @property
    def price_range(self):
        min_price = min(self.variants, key=lambda x: x.price)
        max_price = max(self.variants, key=lambda x: x.price)
        return [min_price, max_price]

    @property
    def preview(self):
        for variant in self.variants:
            for picture in variant.pictures:
                if picture.is_preview:
                    return picture


class ItemVariant(models.Model):
    item_family = models.ForeignKey(
        to=ItemFamily, on_delete=models.DO_NOTHING, related_name='variants'
    )
    name = models.CharField(max_length='25')
    price = models.FloatField()
    stock = models.IntegerField()
    discount = models.IntegerField(default=25)
    description = models.TextField(max_length=1000, blank=True)

    def get_description(self):
        if self.description:
            return self.description
        else:
            return self.item_family.description


class Picture(models.Model):
    item_variant = models.ForeignKey(
        to=ItemVariant, on_delete=models.DO_NOTHING, related_name='pictures'
    )
    image = models.ImageField()
    is_preview = models.BooleanField()
