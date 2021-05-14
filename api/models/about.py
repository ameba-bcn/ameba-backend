from django.db import models


class About(models.Model):
    text = models.TextField()
    is_active = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
