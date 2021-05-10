from django import dispatch
from django.db.models import signals

from api.models import Payment, Membership

subscription_purchased = dispatch.Signal(
    providing_args=['member', 'subscription']
)


@dispatch.receiver(signals.post_save, sender=Payment)
def on_new_subscription(member, subscription):
    pass