from django.db import models


class Membership(models.Model):
    number = models.IntegerField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()
