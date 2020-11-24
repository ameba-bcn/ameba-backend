from django.db import models
from django.utils import timezone


DEFAULT_DURATION = 365


class Membership(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=DEFAULT_DURATION)
    expires = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.expires = timezone.now() + DEFAULT_DURATION
        return super().save(*args, **kwargs)
