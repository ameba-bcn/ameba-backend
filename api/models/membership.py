from django.db import models
from django.utils import timezone


DEFAULT_DURATION = 365


class Membership(models.Model):
    member = models.ForeignKey(
        'Member', on_delete=models.CASCADE, related_name='memberships'
    )
    created = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=DEFAULT_DURATION)
    expires = models.DateTimeField(blank=True)
    subscription = models.ForeignKey(
        'Subscription', on_delete=models.DO_NOTHING, related_name='memberships'
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.expires = timezone.now() + DEFAULT_DURATION
        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires

    @property
    def is_active(self):
        return not self.is_expired
