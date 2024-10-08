from background_task import background
from django.db.models import Q
from django.conf import settings

from api import qr_generator
from api import qr_factories
from api.email_factories import BeforeRenewalNotification
from api.models import Membership
from api.signals import emails
from api import email_factories


@background(schedule=0)
def check_and_notify_before_renewal(membership_id):
    if not Membership.objects.filter(id=membership_id):
        return

    membership = Membership.objects.get(id=membership_id)
    user = membership.member.user

    if membership.is_active and user.is_active:
        BeforeRenewalNotification.send_to(
            mail_to=user.email,
            user=user,
            subscription=membership.subscription,
            membership=membership
        )


@background(schedule=0)
def expire_if_didnt_renew(membership_id):
    if not Membership.objects.filter(id=membership_id):
        return

    membership = Membership.objects.get(id=membership_id)
    member = membership.member
    user = member.user

    for same_subs in Membership.objects.filter(
            member=member, subscription=membership.subscription
    ):
        if same_subs.is_active:
            return

    if membership.is_expired:
        user.groups.remove(membership.subscription.group)
        # todo: notify user!!


@background(schedule=0)
def generate_email_with_qr_and_notify(membership_id):
    membership = Membership.objects.get(pk=membership_id)
    user = membership.member.user

    if user.member.memberships.filter(
        ~Q(pk=membership.pk), subscription=membership.subscription
    ):
        email_factories.RenewalConfirmation.send_to(
            mail_to=user.email,
            user=user,
            subscription=membership.subscription,
            site_name=settings.HOST_NAME,
            protocol=settings.DEBUG and 'http' or 'https'
        )
    else:
        email_factories.NewMembershipEmail.send_to(
            mail_to=user.email,
            user=user,
            subscription=membership.subscription,
            site_name=settings.HOST_NAME,
            protocol=settings.DEBUG and 'http' or 'https'
        )
