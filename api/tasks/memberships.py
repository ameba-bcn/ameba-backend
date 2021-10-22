from background_task import background

from api.email_factories import BeforeRenewalNotification
from api.models import Membership
from api.signals import emails


@background(schedule=0)
def check_and_notify_before_renewal(membership_id):
    if not Membership.objects.filter(id=membership_id):
        return

    membership = Membership.objects.get(id=membership_id)
    user = membership.member.user

    if membership.is_active and user.is_active:
        BeforeRenewalNotification.send_to(user=user, membership=membership)


@background(schedule=0)
def renew_membership(membership_id):
    if not Membership.objects.filter(id=membership_id):
        return

    membership = Membership.objects.get(id=membership_id)

    if not membership.member.user.is_active:
        return

    # todo: Payment renewal here!
    payment_successful = True

    if not payment_successful:
        emails.on_failed_renewal.send(
            sender=Membership,
            user=membership.member.user,
            membership=membership
        )

    # If renewal payment is successful...
    if membership.auto_renew:
        member = membership.member
        member.memberships.add(
            subscription=membership.subscription
        )
