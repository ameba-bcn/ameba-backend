from django.db import models
from django.db.models import Sum

from api.models import Item

GENRE_CHOICES = (
    ('unisex', 'unisex'),
    ('men', 'men'),
    ('women', 'women')
)


class Article(Item):

    @property
    def total_stock(self):
        if self.sizes.all().exists():
            return self.sizes.aggregate(Sum('stock'))['stock__sum']
        return self.stock

    @property
    def has_stock(self):
        return bool(self.total_stock)


class ArticleSize(models.Model):
    size = models.CharField(max_length=3)
    genre = models.CharField(max_length=6, choices=GENRE_CHOICES, blank=True)
    article = models.ForeignKey(
        to=Article, on_delete=models.CASCADE, related_name='sizes'
    )
    stock = models.IntegerField()

    def __str__(self):
        return f'{self.size} ({self.genre})'
