from api.tests._helpers import BaseTest, check_structure
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models.cart import Cart
from api.models.user import User


class CartFlowTests(BaseTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'
    LIST_ENDPOINT = '/api/carts/'

    @staticmethod
    def get_user(user_tag=None):
        user_props = {
            'username': f'User {user_tag or 0}',
            'password': 'passwordsitomio',
            'email': f'amebauser_{user_tag or 0}@ameba.cat',
            'is_active': True
        }
        return User.objects.create(**user_props)

    @staticmethod
    def get_token(user):
        return RefreshToken.for_user(user)

    @staticmethod
    def get_cart(user=None, items=None):
        cart = Cart.objects.create(user=user)
        if items:
            cart.items.set(items)
        return cart

    @staticmethod
    def check_ownership(cart, user):
        cart.refresh_from_db()
        return cart.user == user

    def test_get_no_auth_no_owned_id_cart_returns_200(self):
        cart = self.get_cart()
        response = self._get(pk=cart.pk)

        response_struct = {
            "id": str(cart.id),
            "user": None,
            "total": "0.00 €",
            "count": 0,
            "cart_items": [],
            "discount_code": None
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, response_struct)

    def test_get_no_auth_no_owned_current_cart_returns_401(self):
        response = self._get(pk='current')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_no_auth_owned_others_id_cart_returns_401(self):
        user = self.get_user()
        cart = self.get_cart(user=user)
        response = self._get(pk=cart.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_auth_no_owned_id_cart_returns_200_and_get_ownership(self):
        user = self.get_user()
        token = self.get_token(user)
        cart = self.get_cart()
        response = self._get(pk=cart.id, token=token.access_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.check_ownership(cart, user))

    def test_get_auth_no_owned_current_cart_returns_200_and_get_ownership(self):
        user = self.get_user()
        token = self.get_token(user)

        response = self._get(pk='current', token=token.access_token)

        def get_user_cart():
            return user.cart

        self.assertRaises(expected_exception=Cart.DoesNotExist(),
                          callable=get_user_cart)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.cart)

    def test_get_auth_owned_id_cart_returns_200(self):
        assert False

    def test_get_auth_owned_others_id_cart_returns_401(self):
        assert False

    def test_get_auth_owned_current_cart_returns_200(self):
        assert False

    def test_create_cart_no_auth(self):
        assert False

    def test_create_current_cart_auth(self):
        assert False

    def test_create_cart_auth_returns_current_cart(self):
        assert False

    def test_create_cart_wrong_auth_gives_401(self):
        assert False

    def test_patch_cart_items_no_auth(self):
        assert False

    def test_patch_cart_no_items_list_no_auth_doesnt_change_cart(self):
        assert False

    def test_patch_cart_empty_items_list_no_auth_empty_cart(self):
        assert False

    def test_patch_current_cart_auth(self):
        assert False

    def test_patch_current_cart_empty_items_list_empty_cart(self):
        assert False

    def test_patch_current_cart_no_items_list_doesnt_change_current_cart(self):
        assert False

    def test_patch_id_cart_auth_sets_id_cart_as_current(self):
        assert False
