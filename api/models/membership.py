from django.db import models
from django.utils import timezone


DURATION = 365
ABOUT_TO_EXPIRE_DAYS = 30


class MembershipStates:
    expires_soon = 'expires_soon'
    expired = 'expired'
    active = 'active'
    not_active_yet = 'not_active_yet'


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

    @property
    def expires_soon(self):
        return self.starts < timezone.now() < self.expires - timezone.timedelta(days=DURATION)

    @property
    def state(self):
        if self.expires_soon:
            return MembershipStates.expires_soon
        elif self.is_expired:
            return MembershipStates.expired
        elif not self.is_active:
            return MembershipStates.not_active_yet
        return MembershipStates.active
