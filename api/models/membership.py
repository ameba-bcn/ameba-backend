from django.db import models
from django.utils import timezone


DURATION = 365


class Membership(models.Model):
    member = models.ForeignKey(
        'Member', on_delete=models.CASCADE, related_name='memberships'
    )
    created = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=DURATION)
    starts = models.DateTimeField(default=timezone.now)
    expires = models.DateTimeField(blank=True)
    subscription = models.ForeignKey(
        'Subscription', on_delete=models.DO_NOTHING, related_name='memberships'
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.expires = self.starts + timezone.timedelta(days=DURATION)
        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires

    @property
    def is_active(self):
        return self.starts < timezone.now() < self.expires
