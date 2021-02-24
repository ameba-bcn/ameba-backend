import time

from api.tests._helpers import BaseTest, check_structure
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models.cart import Cart
from api.models.user import User
from api.models import Item


class BaseCartTest(BaseTest):
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


class TestGetCart(BaseCartTest):

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.check_ownership(cart, user))

    def test_get_auth_no_owned_current_cart_returns_200_and_get_ownership(self):
        user = self.get_user()
        self.assertIsNone(user.cart)

        token = self.get_token(user)
        response = self._get(pk='current', token=token.access_token)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user.refresh_from_db()
        self.assertTrue(user.cart)

    def test_get_auth_owned_id_cart_returns_200(self):
        user = self.get_user()
        token = self.get_token(user)
        cart = self.get_cart(user)

        response = self._get(pk=cart.id, token=token.access_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_auth_owned_others_id_cart_returns_401(self):
        user = self.get_user()
        user_2 = self.get_user(2)
        token = self.get_token(user)
        cart = self.get_cart(user_2)

        response = self._get(pk=cart.id, token=token.access_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_auth_owned_current_cart_returns_200(self):
        user = self.get_user()
        token = self.get_token(user)
        cart = self.get_cart(user)

        response = self._get(pk='current', token=token.access_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], str(cart.id))


class TestPostCarts(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'
    LIST_ENDPOINT = '/api/carts/'

    def _create_items(self, items):
        if items:
            for item in items:
                cart_data = dict(
                    id=item,
                    name=f'item_{item}',
                    description=f'This is the item {item}',
                    price=item * 10,
                    stock=item,
                )
                Item.objects.create(**cart_data)

    def _get_body(self, items, other_keys):
        body = {}
        if type(items) is list:
            body['items'] = items
            self._create_items(items)
        if other_keys:
            for key in other_keys:
                body[key] = 'whatever value'
        return body

    def _perform_request(self, auth, previous_cart, body):
        token = None
        cart = None
        if auth:
            user = self.get_user()
            token = self.get_token(user).access_token
            if previous_cart:
                cart = self.get_cart(user)
        response = self._create(props=body, token=token)
        if cart:
            self.assertTrue(response.data.get('id', False))
            self.assertNotEqual(response.data.get('id', None), str(cart.id))
        return response

    def _check_response_body(self, items, response):
        self.assertEqual(len(items or []), response.data['count'])

    def _execute_test(self, test_attrs):
        body = self._get_body(test_attrs['items'], test_attrs['other_keys'])
        response = self._perform_request(
            auth=test_attrs['auth'],
            previous_cart=test_attrs['previous_cart'],
            body=body
        )
        self.assertEqual(response.status_code, test_attrs['returns'])
        self._check_response_body(test_attrs['items'], response)

    def test_post_no_auth_no_items_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            items=None,
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_no_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            items=None,
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_items_key_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            items=[],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_items_key_other_keys_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            items=[],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_items_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            items=[1, 2],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            items=[1, 2],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_no_items_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            items=None,
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_no_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            items=None,
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_items_key_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            items=[],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_items_key_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            items=[],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_items_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            items=[1, 2],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            items=[1, 2],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_cart_no_items_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            items=None,
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_no_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            items=None,
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_items_key_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            items=[],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_items_key_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            items=[],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_items_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            items=[1, 2],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            items=[1, 2],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)
