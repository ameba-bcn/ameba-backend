import django.dispatch as dispatch
import django.db.models.signals as signals

import api.models as api_models
import api.stripe as api_stripe


@dispatch.receiver(signals.post_save, sender=api_models.Discount)
def add_stripe_discount(sender, instance, created, **kwargs):
    api_stripe.get_create_update_discount(discount=instance)


@dispatch.receiver(signals.post_delete, sender=api_models.Discount)
def delete_stripe_discount(sender, instance, **kwargs):
    api_stripe.delete_discount(discount=instance)
