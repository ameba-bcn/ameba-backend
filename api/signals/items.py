import django.dispatch
import django.db.models.signals as signals
from django.conf import settings

import api.signals.events as event_signals
import api.signals.memberships as membership_signals
import api.models as api_models
import api.stripe as stripe


@django.dispatch.receiver(signals.m2m_changed,
                          sender=api_models.ItemVariant.acquired_by.through)
def process_acquired_items(instance, pk_set, action, model, **kwargs):
    if action == 'post_add':
        order = None
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

