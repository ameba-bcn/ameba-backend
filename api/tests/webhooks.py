import api.tests.helpers.carts as cart_helpers
import api.tests.helpers.user as user_helpers
import api.tests.helpers.items as item_helpers
import api.tests._helpers as helpers


class TestStripeWebhooks(helpers.BaseTest):

    def test_succeeded_pre_existing_payment_closes_payment(self):
        user = user_helpers.get_user(
            username='Choco', email='choko@frito.com', password='12345'
        )
