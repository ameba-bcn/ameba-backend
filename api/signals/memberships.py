from django import dispatch
import django.db.models.signals as signals

from api.models import Membership
from api.bg_tasks.notifications import (
    notify_member_about_to_expire, notify_member_expired
)
from api.signals import new_member

subscription_purchased = dispatch.Signal(
    providing_args=['member', 'subscription']
)


@dispatch.receiver(subscription_purchased)
def create_membership(sender, member, subscription, **kwargs):
    active_ms = Membership.objects.filter(member=member).order_by(
        '-expires').first()
    attrs = dict(member=member, subscription=subscription)
    if active_ms and not active_ms.is_expired():
        attrs['starts'] = active_ms.expires
    membership = Membership.objects.create(**attrs)
    membership.member.user.groups.add(subscription.group)


@dispatch.receiver(signals.post_save, sender=Membership)
def trigger_new_member_notifications(sender, instance, created, **kwargs):
    if created:
        # Trigger reminders
        notify_member_about_to_expire(schedule=0)
        notify_member_expired(schedule=0)

        # Trigger new member signal
        new_member.send(sender=Membership, user=instance.member.user,
                        subscription=instance.subscription)
