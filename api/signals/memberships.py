from django import dispatch

from api.models import Membership

subscription_purchased = dispatch.Signal(
    providing_args=['member', 'subscription']
)


@dispatch.receiver(subscription_purchased)
def on_new_subscription(sender, member, subscription, **kwargs):
    active_ms = Membership.objects.filter(member=member).order_by(
        '-expires').first()
    attrs = dict(member=member, subscription=subscription)
    if active_ms and not active_ms.is_expired():
        attrs['starts'] = active_ms.expires
    membership = Membership.objects.create(**attrs)
    membership.member.user.groups.add(subscription.group)

