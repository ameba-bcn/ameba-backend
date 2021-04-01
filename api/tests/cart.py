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

    def get_cart(self, user=None, items=None):
        cart = Cart.objects.create(user=user)
        if items:
            self.create_items(items)
            cart.items.set(items)
        return cart

    @staticmethod
    def check_ownership(cart, user):
        cart.refresh_from_db()
        return cart.user == user

    @staticmethod
    def create_items(items):
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
        self.assertIsNone(user.cart)

        token = self.get_token(user)
        response = self._get(pk='current', token=token.access_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.cart)

    def test_get_auth_owned_id_cart_returns_200(self):
        user = self.get_user()
        token = self.get_token(user)
        cart = self.get_cart(user)

        response = self._get(pk=cart.id, token=token.access_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(cart.id))


class TestPostCarts(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'
    LIST_ENDPOINT = '/api/carts/'

    def _get_body(self, items, other_keys):
        body = {}
        if type(items) is list:
            body['items'] = items
            self.create_items(items)
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


class TestPatchCart(BaseCartTest):

    def _execute_test(self, current_items, new_items, auth, current_label,
                      status_code):

        self.create_items(current_items)
        self.create_items(new_items)

        request_body = None
        if type(new_items) is list:
            request_body = {
                'items': new_items
            }

        token = None
        if auth:
            user = self.get_user()
            token = self.get_token(user).access_token
            cart = self.get_cart(user=user)
        else:
            cart = self.get_cart()

        if current_items:
            for item in current_items:
                cart.items.add(item)

        cart_id = current_label or cart.id
        response = self._partial_update(
            pk=cart_id, token=token, props=request_body
        )

        self.assertEqual(response.status_code, status_code)

        if type(new_items) is list:
            cart_count = len(new_items)
        elif current_items:
            cart_count = len(current_items)
        else:
            cart_count = 0

        self.assertEqual(response.data['count'], cart_count)
        self.assertEqual(response.data['id'], str(cart.id))

    def test_patch_anon_existing_empty_cart_gets_updated_with_items(self):
        current_items = []
        new_items = [1, 2]
        auth = False
        current_label = False
        status_code = status.HTTP_200_OK

        self._execute_test(current_items, new_items, auth, current_label,
                           status_code)

    def test_patch_anon_existing_empty_cart_stays_empty_no_items(self):
        current_items = []
        new_items = None
        auth = False
        current_label = False
        status_code = status.HTTP_200_OK

        self._execute_test(current_items, new_items, auth, current_label,
                           status_code)

    def test_patch_anon_existing_cart_stays_equal_no_items_key(self):
        current_items = [1, 2]
        new_items = None
        auth = False
        current_label = False
        status_code = status.HTTP_200_OK

        self._execute_test(current_items, new_items, auth, current_label,
                           status_code)

    def test_path_anon_existing_cart_empty_after_sending_empty_items_list(self):
        current_items = [1, 2]
        new_items = []
        auth = False
        current_label = False
        status_code = status.HTTP_200_OK

        self._execute_test(current_items, new_items, auth, current_label,
                           status_code)

    def test_path_auth_current_label_updates_user_cart(self):
        current_items = [1, 2]
        new_items = []
        auth = True
        current_label = 'current'
        status_code = status.HTTP_200_OK

        self._execute_test(current_items, new_items, auth, current_label,
                           status_code)

    def test_path_auth_current_id_updates_user_cart(self):
        current_items = [1, 2]
        new_items = []
        auth = True
        current_label = None
        status_code = status.HTTP_200_OK

        self._execute_test(current_items, new_items, auth, current_label,
                           status_code)

    def test_path_auth_anon_cart_replaces_old_user_cart(self):
        user = self.get_user()
        token = self.get_token(user)
        user_cart = self.get_cart(user)
        cart = self.get_cart()

        response = self._partial_update(
            pk=cart.id, token=token.access_token, props={}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.cart.id, cart.id)
        self.assertFalse(Cart.objects.filter(id=user_cart.id).exists())

    def test_path_auth_current_label_creates_new_cart_for_user(self):
        user = self.get_user()
        token = self.get_token(user).access_token
        body = {'items': [1, 2]}
        self.create_items(body['items'])

        response = self._partial_update('current', token, body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], len(body['items']))

    def test_path_auth_others_cart_not_allowed(self):
        user = self.get_user(1)
        token = self.get_token(user).access_token

        body = {'items': [1, 2]}

        user_2 = self.get_user(2)
        token_2 = self.get_token(user_2).access_token
        cart_2 = self.get_cart(user=user_2, items=body.get('items'))

        response = self._partial_update(cart_2.id, token, body)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response_2 = self._get(pk=cart_2.id, token=token_2)
        self.assertEqual(response_2.data['count'], len(body.get('items')))


class TestCartCheckout(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/checkout/'

    def test_not_authenticated_checkout_returns_401(self):
        cart = self.get_cart(items=[1, 2])
        response = self._get(pk=cart.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
