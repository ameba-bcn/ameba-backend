from datetime import timedelta

from django import dispatch
import django.db.models.signals as signals

from api.models import Membership
from api.signals import new_membership
from api.tasks import memberships
import api.stripe as api_stripe

subscription_purchased = dispatch.Signal(
    providing_args=['member', 'subscription']
)


@dispatch.receiver(subscription_purchased)
def create_membership(sender, member, subscription, **kwargs):
    active_ms = Membership.objects.filter(member=member).order_by(
        '-expires').first()
    attrs = dict(member=member, subscription=subscription)
    if active_ms and not active_ms.is_expired:
        attrs['starts'] = active_ms.expires
    membership = Membership.objects.create(**attrs)
    api_stripe.cancel_previous_subscriptions(
        user=member.user, subscription=subscription
    )
    membership.member.user.groups.add(subscription.group)


@dispatch.receiver(signals.post_save, sender=Membership)
def trigger_new_member_notifications(sender, instance, created, **kwargs):
    if created:
        # Trigger reminders
        # Schedule before renewal notification
        before_renewal_time = instance.expires - timedelta(days=30)
        memberships.check_and_notify_before_renewal(
            membership_id=instance.id,
            schedule=before_renewal_time
        )
        # memberships.renew_membership(
        #     membership_id=instance.id, schedule=instance.expires
        # )

        # Trigger new member signal
        new_membership.send(
            sender=Membership,
            user=instance.member.user,
            membership=instance
        )

