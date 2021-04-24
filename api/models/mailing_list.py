from django.db import models
from django.conf import settings


class MailingList(models.Model):
    address = models.CharField(max_length=120)
