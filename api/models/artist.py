from django.db import models
from django.utils.translation import gettext as _


class Artist(models.Model):
    name = models.CharField(max_length=50)
    biography = models.TextField(max_length=2500)
