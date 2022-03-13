from datetime import timedelta

from django import dispatch
import django.db.models as models

import api.models as api_models
from api.signals import new_membership
from api.tasks import memberships
import api.stripe as api_stripe

subscription_purchased = dispatch.Signal(
    providing_args=['member', 'subscription']
)


@dispatch.receiver(subscription_purchased)
def create_membership(sender, member, subscription, **kwargs):
    attrs = dict(member=member, subscription=subscription)
    api_models.Membership.objects.create(**attrs)


@dispatch.receiver(models.signals.post_save, sender=api_models.Membership)
def trigger_new_member_notifications(sender, instance, created, **kwargs):
    if created:
        # Trigger reminders
        # Schedule before renewal notification
        before_renewal_time = instance.expires - timedelta(days=30)
        memberships.check_and_notify_before_renewal(
            membership_id=instance.id,
            schedule=before_renewal_time
        )
        margin_renewal_time = instance.expires + timedelta(days=1)

        # Schedule expiration check
        memberships.expire_if_didnt_renew(
            membership_id=instance.id,
            schedule=margin_renewal_time
        )

        if instance.is_active:
            # Add to corresponding group
            instance.member.user.groups.add(instance.subscription.group)

        # Cancel previous different subscriptions in case they exist
        api_stripe.cancel_previous_subscriptions(
            user=instance.member.user, subscription=instance.subscription
        )

        # Trigger new member signal
        new_membership.send(
            sender=api_models.Membership,
            user=instance.member.user,
            membership=instance
        )

