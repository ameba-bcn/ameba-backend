from django.utils import timezone
from django.core.files.images import ImageFile
from rest_framework import status
from django.test import tag
from django.contrib.auth.models import Group

from api.tests._helpers import BaseTest, check_structure
from api.tests.helpers import user as user_helpers
from api.tests.user import BaseUserTest
from api.models import Article, Image
from api.models import Event, User, Image, Item


class TestSavedUserEvents(BaseTest):
    """ Events """
    LIST_ENDPOINT = '/api/users/current/events/signed_up/'
    DETAIL_ENDPOINT = '/api/users/current/events/signed_up/{pk}/'

    CART_ENDPOINT = '/api/carts/current/'
    CART_CHECKOUT = '/api/carts/current/checkout/'

    def test_user_adquires_event_apears_in_acquired_by(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user = user_helpers.get_user(**user_data)
        token = user_helpers.get_user_token(user)
        # Create event + variants
        item_variant = next(user_helpers.create_items_variants(
            item_variants=[1], for_free=True, item_class=Event
        ))
        response = self.request(
            url=self.CART_ENDPOINT,
            method='patch',
            token=token,
            props={'item_variant_ids': [1]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.request(
            url=self.CART_CHECKOUT,
            method='get',
            token=token,
            props={}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.request(
            url=self.CART_ENDPOINT,
            method='delete',
            token=token,
            props={}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self._list(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
