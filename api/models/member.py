from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.db import models
from api.models.membership import MembershipStates


# Get current user model
User = get_user_model()


def get_default_number():
    if not Member.objects.all():
        return 100
    else:
        return Member.objects.all().order_by('-number').first().number + 1


class Member(models.Model):
    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')

    number = models.IntegerField(
        primary_key=True, editable=True, default=get_default_number,
        verbose_name=_('number')
    )
    user = models.OneToOneField(
        to='User', on_delete=models.CASCADE, verbose_name=_('user'),
        related_name='member'
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_('address')
    )
    first_name = models.CharField(max_length=20, verbose_name=_('first name'))
    last_name = models.CharField(max_length=20, verbose_name=_('last name'))
    phone_number = models.CharField(
        max_length=10, verbose_name=_('phone number')
    )

    def get_newest_membership(self):
        if self.memberships.all():
            return self.memberships.order_by('-expires').first()
        return None

    @property
    def status(self):
        if newest_membership := self.get_newest_membership():
            if newest_membership.state == MembershipStates.not_active_yet:
                return MembershipStates.active
            return newest_membership.state
        return None

    @property
    def type(self):
        if newest_membership := self.get_newest_membership():
            return newest_membership.subscription.name
        return None
