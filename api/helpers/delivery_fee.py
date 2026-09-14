from api.models import CartItems, ItemVariant

DELIVERY_FEE_CENTS = 400


def ensure_delivery_fee(cart) -> None:
    """Add the DeliveryFee CartItem if not already present (idempotent)."""
    variant = ItemVariant.objects.get(is_delivery_fee=True)
    CartItems.objects.get_or_create(cart=cart, item_variant=variant)


def remove_delivery_fee(cart) -> None:
    """Remove the DeliveryFee CartItem if present (no-op if none exist)."""
    variant = ItemVariant.objects.get(is_delivery_fee=True)
    CartItems.objects.filter(cart=cart, item_variant=variant).delete()
