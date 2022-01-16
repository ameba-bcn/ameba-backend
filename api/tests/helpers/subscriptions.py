import random

import api.tests.helpers.items as item_helpers
import api.models as api_models


def create_subscription(name='ameba_member'):
    return item_helpers.create_item(
        name=name,
        item_class=api_models.Subscription
    )


def subscribe_member(member, duration=365, subscription_name='ameba_member'):
    subscription = create_subscription(subscription_name)
    return api_models.Membership.objects.create(
        member=member, duration=duration, subscription=subscription
    )
