from django.db import models


class Language(models.Model):
    code = models.CharField(unique=True, max_length=5)
    name = models.TextField(blank=True, max_length=50)
