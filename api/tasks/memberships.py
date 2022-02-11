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
def generate_email_with_qr_and_notify(membership_id):
    membership = Membership.objects.get(pk=membership_id)
    user = membership.member.user
    # Generate pdf with qr here
    qr_path = qr_generator.generate_member_card_qr(
        member=membership.member,
        protocol=settings.DEBUG and 'http' or 'https',
        site_name=settings.HOST_NAME
    )
    pdf_card = qr_factories.MemberCardWithQr(
        identifier=membership.member.pk,
        member=membership.member,
        qr_path=qr_path
    )

    if user.member.memberships.filter(
        ~Q(pk=membership.pk), subscription=membership.subscription
    ):
        email_factories.RenewalConfirmation.send_to(
            attachment=pdf_card.attachment,
            mail_to=user.email,
            user=user,
            subscription=membership.subscription,
            site_name=settings.HOST_NAME,
            protocol=settings.DEBUG and 'http' or 'https'
        )
    else:
        email_factories.NewMembershipEmail.send_to(
            attachment=pdf_card.attachment,
            mail_to=user.email,
            user=user,
            subscription=membership.subscription,
            site_name=settings.HOST_NAME,
            protocol=settings.DEBUG and 'http' or 'https'
        )
