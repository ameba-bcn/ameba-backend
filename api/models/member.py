import datetime

from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import signing
from django.db import models
from localflavor.es.models import ESIdentityCardNumberField

from api import qr_generator
from api.models.membership import MembershipStates


# Get current user model
User = get_user_model()


QR_DATE_FORMAT = 'Y%m%d%H%M%S'


def get_default_number():
    if not Member.objects.all():
        return 1
    else:
        return Member.objects.all().order_by('-number').first().number + 1


def get_default_qr_date():
    return datetime.datetime.now().strftime(QR_DATE_FORMAT)


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
    identity_card = ESIdentityCardNumberField(verbose_name='dni/nie')
    first_name = models.CharField(max_length=20, verbose_name=_('first name'))
    last_name = models.CharField(max_length=20, verbose_name=_('last name'))
    phone_number = models.CharField(
        max_length=10, verbose_name=_('phone number')
    )
    qr_date = models.CharField(max_length=14, default=get_default_qr_date)

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

    def get_member_card_token(self):
        self.qr_date = datetime.datetime.now().strftime(QR_DATE_FORMAT)
        signature = (
            self.pk,
            self.qr_date
        )
        return signing.dumps(signature, salt=settings.QR_MEMBER_SALT)
