import django.dispatch
import django.db.models.signals as signals
from django.dispatch import receiver

import api.signals.events as event_signals
import api.signals.memberships as membership_signals
import api.models as api_models
import api.stripe as stripe


item_acquired = django.dispatch.Signal(providing_args=['user', 'item_variant'])


@receiver(item_acquired)
def acquired_item(sender, user, item_variant, **kwargs):
    order = None
    if item_variant.item.is_event():
        event_signals.event_acquired.send(
            sender=user.__class__, item_variant=item_variant, user=user
        )

    elif item_variant.item.is_subscription():
        membership_signals.subscription_purchased.send(
            sender=user.__class__,
            member=user.member,
            subscription=item_variant.item.subscription
        )
    elif item_variant.item.is_article():
        if not order:
            order = api_models.Order.objects.create(user=user)
        order.item_variants.add(item_variant)

    if order:
        order.send_new_order_notification()


@django.dispatch.receiver(signals.post_save, sender=api_models.ItemVariant)
def add_product_to_stripe(sender, instance, created, **kwargs):
    # if settings.STRIPE_SYNC:
    stripe.create_or_update_product_and_price(item_variant=instance)

