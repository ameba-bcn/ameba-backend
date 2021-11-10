import django.dispatch
import django.db.models.signals as signals

import api.signals.events as event_signals
import api.signals.memberships as membership_signals
import api.models as api_models

items_acquired = django.dispatch.Signal(providing_args=['cart', 'request'])


@django.dispatch.receiver(signals.m2m_changed,
                          sender=api_models.ItemVariant.acquired_by.through)
def process_adquired_items(instance, pk_set, action, model, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            user = api_models.User.objects.get(id=user_id)
            item_variant = instance

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


@django.dispatch.receiver(items_acquired)
def process_cart_items(sender, cart, request, **kwargs):
    for cart_item in cart.get_cart_items():
        item_variant = cart_item.item_variant
        item_variant.acquired_by.add(cart.user)
