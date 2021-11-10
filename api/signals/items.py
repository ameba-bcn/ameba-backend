import django.dispatch
import django.db.models.signals as signals

import api.signals.events as event_signals
import api.signals.memberships as membership_signals
import api.models as api_models

items_acquired = django.dispatch.Signal(providing_args=['cart', 'request'])


# @django.dispatch.receiver(signals.m2m_changed,
#                           sender=api_models.Item.acquired_by.through)
# def process_adquired_items(instance, pk_set, action, model, **kwargs):
#     if action == 'post_add':
#         for user_id in pk_set:
#             item = instance
#             item_variant = item.item_variant


@django.dispatch.receiver(items_acquired)
def process_cart_items(sender, cart, request, **kwargs):
    for cart_item in cart.get_cart_items():
        item_variant = cart_item.item_variant
        item_variant.acquired_by.add(cart.user)

        if item_variant.item.is_event():
            event_signals.event_acquired.send(
                sender=sender, item_variant=item_variant, user=cart.user,
                request=request
            )

        elif item_variant.item.is_subscription():
            membership_signals.subscription_purchased.send(
                sender=sender,
                member=cart.user.member,
                subscription=cart.subscription
            )

