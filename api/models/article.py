from django.db import models
from django.db.models import Sum

from api.models import Item


class Article(Item):

    def get_stock(self):
        if stock := self.variants.aggregate(Sum('stock'))['stock__sum'] > 0:
            return stock
        else:
            return self.stock


class ArticleVariant(models.Model):
    name = models.CharField(max_length=25)
    item = models.ForeignKey(
        to=Article, on_delete=models.DO_NOTHING, related_name='variants'
    )
    image = models.ManyToManyField(to='Image', blank=True)
    stock = models.IntegerField()
    description = models.TextField(max_length=1000, blank=True)

    def get_description(self):
        if self.description:
            return self.description
        else:
            return self.item.description

    def __str__(self):
        return self.name
