from django.db import models
from django.utils import timezone

DEFAULT_DURATION = 365


class MembershipManager(models.Manager):
    def create_membership(self, user, subscription, duration=None):
        attrs = dict(user=user, subscription=subscription)
        if duration:
            attrs.update(duration=duration)
        membership = self.model.objects.create(**attrs)
        membership.save()


class Membership(models.Model):
    user = models.ForeignKey(
        to='User', on_delete=models.CASCADE, related_name='memberships'
    )
    subscription = models.ForeignKey(
        to='Subscription', on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=DEFAULT_DURATION)

    objects = MembershipManager()

    @property
    def expires(self):
        return self.created + timezone.timedelta(days=DEFAULT_DURATION)

    def is_expired(self):
        return timezone.now() > self.expires

    def is_active(self):
        return not self.is_expired()
