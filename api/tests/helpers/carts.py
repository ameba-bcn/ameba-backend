import api.models as api_models

import api.tests.helpers.items as items_helpers


def get_cart(user=None, item_variants=None, for_free=False,
             item_class=api_models.Item):
    cart = api_models.Cart.objects.create(user=user)
    if item_variants:
        items_helpers.create_items_variants(
            item_variants, for_free=for_free, item_class=item_class
        )
        cart.item_variants.set(item_variants)
    return cart
