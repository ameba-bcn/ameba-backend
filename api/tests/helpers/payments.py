import api.models as api_models


def create_payment(user, cart=None, invoice=None, item_variants=None):
    payment = api_models.Payment.objects.get_or_create_payment(
        user=user, cart=cart, invoice=invoice
    )
    if item_variants:
        payment.item_variants.add(*item_variants)
    return payment
