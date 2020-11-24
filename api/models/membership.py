from django.db import models
from django.utils import timezone


DEFAULT_DURATION = timezone.timedelta(365)


class Membership(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(default=timezone.now() + DEFAULT_DURATION)
