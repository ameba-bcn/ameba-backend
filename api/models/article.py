from django.db import models

from api.models import Item

GENRE_CHOICES = (
    ('unisex', 'unisex'),
    ('men', 'men'),
    ('women', 'women')
)


class ArticleAttributeType(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class ArticleAttribute(models.Model):
    attribute = models.ForeignKey(
        'ArticleAttributeType', on_delete=models.CASCADE
    )
    value = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.attribute.name} - {self.value}'


class ArticleFamily(models.Model):
    name = models.CharField(max_length=100, unique=True)
    images = models.ManyToManyField(to='Image', blank=False)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name


class Article(Item):
    family = models.ForeignKey(
        'ArticleFamily', on_delete=models.CASCADE, related_name='articles'
    )
    attributes = models.ManyToManyField('ArticleAttribute', blank=False)
    name = None

    def __str__(self):
        return f'{self.family.name} - {"/".join([attr.value for attr in self.attributes.all()])}'
