import rest_framework.status as status

import api.tests.helpers.carts as cart_helpers
import api.tests.helpers.user as user_helpers
import api.tests.helpers.items as item_helpers
import api.stripe as stripe
import api.tests._helpers as helpers
import api.mocks.stripe


class TestStripeWebhooks(helpers.BaseTest):
    DETAIL_ENDPOINT = '/api/stripe/'
    LIST_ENDPOINT = '/api/stripe/'

    def test_succeeded_pre_existing_payment_closes_payment(self):
        user = user_helpers.get_user(
            username='Choco', email='choko@frito.com', password='12345'
        )
        cart = cart_helpers.get_cart(user=user, item_variants=[1, 2, 3])
        cart.checkout()
        payment = stripe.get_or_create_payment(cart)

        # Check payment status

        invoice = payment.invoice

        response = api.mocks.stripe.mock_stripe_succeeded_payment(
            self.client, self.DETAIL_ENDPOINT, invoice
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check payment status
