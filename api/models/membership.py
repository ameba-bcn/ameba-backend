from django.utils.translation import gettext as _
from django.db import models
from django.utils import timezone


DURATION = 365
ABOUT_TO_EXPIRE_DAYS = 30


class MembershipStates:
    expires_soon = 'expires_soon'
    expired = 'expired'
    active = 'active'
    not_active_yet = 'not_active_yet'


class MembershipManager(models.Manager):

    @staticmethod
    def create_membership(member, subscription_variant):
        attrs = dict(
            member=member,
            subscription=subscription_variant.item.subscription
        )
        if period := subscription_variant.period:
            attrs['duration'] = period
        return Membership.objects.create(**attrs)


class Membership(models.Model):
    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Memberships')

    member = models.ForeignKey(
        'Member', on_delete=models.CASCADE, related_name='memberships',
        verbose_name=_('member')
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    duration = models.IntegerField(default=DURATION, verbose_name=_('duration'))
    starts = models.DateTimeField(default=timezone.now, verbose_name=_('starts'))
    expires = models.DateTimeField(blank=True, verbose_name=_('expires'))
    subscription = models.ForeignKey(
        'Subscription', on_delete=models.DO_NOTHING,
        related_name='memberships', verbose_name=_('subscription')

    )
    auto_renew = models.BooleanField(default=True)
    objects = MembershipManager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.expires = self.starts + timezone.timedelta(days=self.duration)
        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if self.id:
            return timezone.now() >= self.expires

    @property
    def is_active(self):
        if self.id:
            return self.starts < timezone.now() < self.expires

    @property
    def expires_soon(self):
        if self.id:
            return self.expires - timezone.timedelta(days=ABOUT_TO_EXPIRE_DAYS) < timezone.now() < self.expires

    @property
    def state(self):
        if self.expires_soon:
            return MembershipStates.expires_soon
        elif self.is_expired:
            return MembershipStates.expired
        elif not self.is_active:
            return MembershipStates.not_active_yet
        return MembershipStates.active
