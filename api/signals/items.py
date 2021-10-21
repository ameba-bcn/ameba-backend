import django.dispatch

import api.signals.events as event_signals
import api.signals.memberships as membership_signals

items_acquired = django.dispatch.Signal(providing_args=['cart', 'request'])


@django.dispatch.receiver(items_acquired)
def process_cart_items(sender, cart, **kwargs):
    for cart_item in cart.get_cart_items():
        item_variant = cart_item.item_variant
        item_variant.item.acquired_by.add(cart.user)

        if item_variant.item.is_event():
            event_signals.event_acquired.send(
                sender=sender, item_variant=item_variant, user=cart.user
            )

        elif item_variant.item.is_subscription():
            membership_signals.subscription_purchased.send(
                sender=sender,
                member=cart.user.member,
                subscription=cart.subscription
            )

