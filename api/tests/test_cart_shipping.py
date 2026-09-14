from rest_framework import status

from api.models import ItemVariant
from api.models.cart import CartItems
from api.tests.cart import BaseCartTest


class TestCartShipping(BaseCartTest):

    def test_patch_with_delivery_payload_sets_shipping_and_adds_fee_item(self):
        """Requirements: 3.1, 3.6, 2.1"""
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user)

        body = {
            'shipping': {
                'delivery': {
                    'direccion': 'Calle Mayor 1',
                    'ciudad': 'Barcelona',
                    'telefono': '612345678',
                    'dni': '12345678A',
                }
            }
        }

        response = self._partial_update(pk=cart.id, token=token, props=body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['shipping']['delivery']['direccion'], 'Calle Mayor 1'
        )

        delivery_fee_variant = ItemVariant.objects.filter(is_delivery_fee=True).first()
        self.assertIsNotNone(delivery_fee_variant)

        cart.refresh_from_db()
        self.assertTrue(cart.item_variants.filter(is_delivery_fee=True).exists())

    def test_patch_switching_to_shop_pickup_removes_fee_item(self):
        """Requirements: 3.5, 2.2"""
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user)

        # Set delivery shipping and add the fee item manually
        cart.shipping = {
            'delivery': {
                'direccion': 'Calle Mayor 1',
                'ciudad': 'Barcelona',
                'telefono': '612345678',
                'dni': '12345678A',
            }
        }
        cart.save()

        delivery_fee_variant = ItemVariant.objects.get(is_delivery_fee=True)
        CartItems.objects.get_or_create(cart=cart, item_variant=delivery_fee_variant)

        # Confirm fee is present before switching
        self.assertTrue(cart.item_variants.filter(is_delivery_fee=True).exists())

        body = {'shipping': {'shop_pickup': {'shop': 'Main Store'}}}
        response = self._partial_update(pk=cart.id, token=token, props=body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['shipping']['shop_pickup']['shop'], 'Main Store')

        cart.refresh_from_db()
        self.assertFalse(cart.item_variants.filter(is_delivery_fee=True).exists())

    def test_patch_with_malformed_shipping_payload_returns_400(self):
        """Requirements: 3.4 — empty direccion should be rejected"""
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user)

        body = {
            'shipping': {
                'delivery': {
                    'direccion': '',
                    'ciudad': 'Barcelona',
                    'telefono': '612345678',
                    'dni': '12345678A',
                }
            }
        }

        response = self._partial_update(pk=cart.id, token=token, props=body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_with_both_delivery_and_pickup_returns_400(self):
        """Requirements: 3.4 — both delivery and shop_pickup non-null is invalid"""
        user = self.get_user()
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user)

        body = {
            'shipping': {
                'delivery': {
                    'direccion': 'Calle Mayor 1',
                    'ciudad': 'Barcelona',
                    'telefono': '612345678',
                    'dni': '12345678A',
                },
                'shop_pickup': {'shop': 'Main Store'},
            }
        }

        response = self._partial_update(pk=cart.id, token=token, props=body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_unauthenticated_returns_401(self):
        """Security: unauthenticated PATCH on a user-owned cart must be rejected"""
        user = self.get_user()
        cart = self.get_cart(user=user)

        body = {'shipping': {'shop_pickup': {'shop': 'Main Store'}}}

        # No token passed → unauthenticated request
        response = self._partial_update(pk=cart.id, token=None, props=body)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
