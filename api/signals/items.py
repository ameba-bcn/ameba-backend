import django.dispatch


items_acquired = django.dispatch.Signal(providing_args=['cart', 'request'])


@django.dispatch.receiver(items_acquired)
def on_cart_deleted(sender, cart, **kwargs):
    for cart_item in cart.get_cart_items():
        cart_item.item_variant.item.acquired_by.add(cart.user)
