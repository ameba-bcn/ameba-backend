from django import dispatch
from django.db.models import signals

from api.models import Payment, Membership

subscription_purchased = dispatch.Signal(
    providing_args=['member', 'subscription']
)


@dispatch.receiver(signals.post_save, sender=Payment)
def on_new_subscription(member, subscription):
    active_ms = Membership.objects.filter(member=member).orderby(
        '-expires').first()
    attrs = dict(member=member, subscription=subscription)
    if not active_ms.is_expired():
        attrs['starts'] = active_ms.expires
    Membership.objects.create(**attrs)
