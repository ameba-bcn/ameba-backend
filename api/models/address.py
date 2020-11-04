from django.db import models


class Address(models.Model):
    raw = models.TextField(max_length=255)
    country = models.CharField(max_length=25)
    city = models.CharField(max_length=25)
    street = models.CharField(max_length=25)
    cp = models.IntegerField()
    url = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

