import logging
from datetime import timedelta

from django import dispatch
from django.db import transaction
import django.db.models as models

import api.models as api_models
from api.signals import new_membership
from api.tasks import memberships
import api.stripe as api_stripe

logger = logging.getLogger(__name__)

subscription_purchased = dispatch.Signal(
    providing_args=['member', 'subscription_variant']
)


@dispatch.receiver(subscription_purchased)
def create_membership(sender, member, subscription_variant,
                      membership_starts=None, **kwargs):
    api_models.Membership.objects.create_membership(
        member=member, subscription_variant=subscription_variant,
        starts=membership_starts
    )


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

        # Cancel previous different subscriptions in case they exist. It's a
        # Stripe call: run it once the membership is committed, and don't let
        # a Stripe hiccup undo the membership the member just paid for.
        user, subscription = instance.member.user, instance.subscription

        def _cancel_previous_subscriptions():
            try:
                api_stripe.cancel_previous_subscriptions(
                    user=user, subscription=subscription
                )
            except Exception:
                logger.exception(
                    'Could not cancel previous subscriptions of user %s',
                    user.id
                )
        transaction.on_commit(_cancel_previous_subscriptions)

        # Trigger new member signal
        new_membership.send(
            sender=api_models.Membership,
            user=instance.member.user,
            membership=instance
        )

