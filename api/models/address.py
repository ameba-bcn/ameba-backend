from django.db import models


class Address(models.Model):
    raw = models.TextField(max_length=255)
