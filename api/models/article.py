from django.db import models
from django.db.models import Sum

from api.models import Item

GENRE_CHOICES = (
    ('unisex', 'unisex'),
    ('men', 'men'),
    ('women', 'women')
)


class Article(Item):

    def get_stock(self):
        if stock := self.sizes.aggregate(Sum('stock'))['stock__sum'] > 0:
            return stock
        else:
            return self.stock


class ArticleSize(models.Model):
    size = models.CharField(max_length=3)
    genre = models.CharField(max_length=6, choices=GENRE_CHOICES, blank=True)
    article = models.ForeignKey(
        to=Article, on_delete=models.DO_NOTHING, related_name='sizes'
    )
    stock = models.IntegerField()

    def __str__(self):
        return f'{self.size} ({self.genre})'
