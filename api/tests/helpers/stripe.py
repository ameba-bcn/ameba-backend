import api.tests.helpers.items as item_helpers
import api.tests.helpers.fixtures.stripe.invoice as invoice_fix
import api.stripe as api_stripe


def get_invoice(user, item_variants, status='paid', sync=False):
    return invoice_fix.get_invoice(user=user, item_variants=item_variants,
                                   status=status)
