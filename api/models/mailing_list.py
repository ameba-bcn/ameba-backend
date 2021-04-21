from django.db import models


class MailingList(models.Model):
    address = models.CharField(max_length=120)


class Subscriber(models.Model):
    email = models.EmailField()
