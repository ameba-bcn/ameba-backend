import time
from django.contrib.auth.models import Group
from api.tests._helpers import BaseTest, check_structure
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models.cart import Cart
from api.models.user import User
from api.models import (
    Item, ItemVariant, ItemAttribute, ItemAttributeType, Subscription, Member
)


class BaseCartTest(BaseTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'
    LIST_ENDPOINT = '/api/carts/'
    CHECKOUT_ENDPOINT = '/api/carts/{pk}/checkout/'

    @staticmethod
    def get_user(user_tag=None, member_profile=False):
        user_props = {
            'username': f'User {user_tag or 0}',
            'password': 'passwordsitomio',
            'email': f'amebauser_{user_tag or 0}@ameba.cat',
            'is_active': True
        }

        user = User.objects.create(**user_props)

        if member_profile:
            Member.objects.create(
                user=user,
                address='whatever address is the place',
                first_name='Obvious',
                last_name='Lee',
                phone_number='123456789'
            )
        return user

    @staticmethod
    def get_token(user):
        return RefreshToken.for_user(user)

    def checkout(self, pk='current', token=None):
        self._authenticate(token=token)
        return self.client.get(self.CHECKOUT_ENDPOINT.format(pk=pk))

    def get_cart(self, user=None, item_variants=None, for_free=False,
                 item_class=Item):
        cart = Cart.objects.create(user=user)
        if item_variants:
            self.create_items_variants(item_variants, for_free=for_free,
                                       item_class=item_class)
            cart.item_variants.set(item_variants)
        return cart

    @staticmethod
    def check_ownership(cart, user):
        cart.refresh_from_db()
        return cart.user == user

    def create_items_variants(self, item_variants, for_free=False,
                              item_class=Item):
        if item_variants:
            item_id = item_variants[0]
            attrs = dict(
                id=item_id,
                name=f'item_{item_id}',
                description=f'This is the item {item_id}',
                is_active=True
            )
            if item_class is Subscription:
                group, created = Group.objects.get_or_create(
                    name='ameba_member'
                )
                attrs['group'] = group

            item = item_class.objects.create(**attrs)
            for item_variant in item_variants:
                cart_data = dict(
                    id=item_variant,
                    item=item,
                    price=0 if for_free else item_variant * 10,
                    stock=item_variant
                )
                item_variant = ItemVariant.objects.create(**cart_data)
                self.create_attributes(item_variant)

    def create_attributes(self, item_variant):
        color = ItemAttributeType.objects.create(name='color')
        size = ItemAttributeType.objects.create(name='size')
        for att, value in (
            (color, 'red'), (size, 'm'), (color, 'green'), (size, 'l')
        ):
            attribute = ItemAttribute.objects.create(attribute=att,
                                                     value=value)
            item_variant.attributes.add(attribute)


class TestGetCart(BaseCartTest):

    def test_get_no_auth_no_owned_id_cart_returns_200(self):
        cart = self.get_cart()
        response = self._get(pk=cart.pk)

        response_struct = {
            "id": str(cart.id),
            "user": None,
            "total": "0.00 €",
            "count": 0,
            "item_variants": [],
            "item_variant_ids": [],
            "discount_code": None,
            "state": {
                "is_payment_succeeded": False,
                "has_user": False,
                "has_member_profile": False,
                "has_memberships": False,
                "has_articles": False,
                "has_events": False,
                "has_subscriptions": False,
                "needs_checkout": True
            }
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
            body['item_variant_ids'] = items
            self.create_items_variants(items)
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
        body = self._get_body(test_attrs['item_variant_ids'], test_attrs['other_keys'])
        response = self._perform_request(
            auth=test_attrs['auth'],
            previous_cart=test_attrs['previous_cart'],
            body=body
        )
        self.assertEqual(response.status_code, test_attrs['returns'])
        self._check_response_body(test_attrs['item_variant_ids'], response)

    def test_post_no_auth_no_items_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            item_variant_ids=None,
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_no_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            item_variant_ids=None,
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_items_key_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            item_variant_ids=[],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_items_key_other_keys_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            item_variant_ids=[],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_items_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            item_variant_ids=[1, 2],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_no_auth_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=False,
            previous_cart=False,
            item_variant_ids=[1, 2],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_no_items_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            item_variant_ids=None,
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_no_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            item_variant_ids=None,
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_items_key_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            item_variant_ids=[],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_items_key_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            item_variant_ids=[],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_items_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            item_variant_ids=[1, 2],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=False,
            item_variant_ids=[1, 2],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_cart_no_items_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            item_variant_ids=None,
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_no_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            item_variant_ids=None,
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_items_key_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            item_variant_ids=[],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_items_key_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            item_variant_ids=[],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_items_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            item_variant_ids=[1, 2],
            other_keys=None,
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)

    def test_post_auth_with_previous_items_other_keys_returns_200(self):
        test_attrs = dict(
            auth=True,
            previous_cart=True,
            item_variant_ids=[1, 2],
            other_keys=['my_key', 'cart', 'user'],
            returns=status.HTTP_201_CREATED
        )
        self._execute_test(test_attrs)


class TestPatchCart(BaseCartTest):

    def _execute_test(self, current_items, new_items, auth, current_label,
                      status_code):

        self.create_items_variants(current_items)
        self.create_items_variants(new_items)

        request_body = None
        if type(new_items) is list:
            request_body = {
                'item_variant_ids': new_items
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
                cart.item_variants.add(item)

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
        body = {'item_variant_ids': [1, 2]}
        self.create_items_variants(body['item_variant_ids'])

        response = self._partial_update('current', token, body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], len(body['item_variant_ids']))

    def test_path_auth_others_cart_not_allowed(self):
        user = self.get_user(1)
        token = self.get_token(user).access_token

        body = {'item_variant_ids': [1, 2]}

        user_2 = self.get_user(2)
        token_2 = self.get_token(user_2).access_token
        cart_2 = self.get_cart(user=user_2, item_variants=body.get('item_variant_ids'))

        response = self._partial_update(cart_2.id, token, body)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response_2 = self._get(pk=cart_2.id, token=token_2)
        self.assertEqual(response_2.data['count'], len(body.get('item_variant_ids')))


class TestCartCheckout(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/checkout/'

    def test_not_authenticated_checkout_returns_401(self):
        cart = self.get_cart(item_variants=[1, 2])
        response = self._get(pk=cart.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cart_with_multiple_subscriptions_returns_400(self):
        user = self.get_user(1, member_profile=True)
        token = self.get_token(user).access_token
        cart = self.get_cart(
            user=user, item_variants=[1, 2], item_class=Subscription
        )
        response = self._get(pk=cart.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cart_with_one_subscription_returns_200(self):
        user = self.get_user(1, member_profile=True)
        token = self.get_token(user).access_token
        cart = self.get_cart(
            user=user, item_variants=[1], item_class=Subscription
        )
        response = self._get(pk=cart.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscription_from_user_without_member_profile_returns_400(self):
        user = self.get_user(1, member_profile=False)
        token = self.get_token(user).access_token
        cart = self.get_cart(
            user=user, item_variants=[1], item_class=Subscription
        )
        response = self._get(pk=cart.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestCartStateFlow(BaseCartTest):
    DETAIL_ENDPOINT = '/api/carts/{pk}/'
    LIST_ENDPOINT = '/api/carts/'

    def test_new_cart_has_no_state(self):
        user = self.get_user(1)
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=[1, 2])
        response = self._get(pk=cart.id, token=token)
        self.assertIn('state', response.data)

        cart_state = response.data.get('state')

        self.assertFalse(cart_state['is_payment_succeeded'])
        self.assertTrue(cart_state['has_user'])
        self.assertFalse(cart_state['has_member_profile'])
        self.assertFalse(cart_state['has_memberships'])
        self.assertFalse(cart_state['has_articles'])
        self.assertFalse(cart_state['has_events'])
        self.assertFalse(cart_state['has_subscriptions'])
        self.assertTrue(cart_state['needs_checkout'])

    def test_changed_cart_requires_checkout_before_payment(self):
        user = self.get_user(1)
        token = self.get_token(user).access_token
        cart = self.get_cart(user=user, item_variants=[1, 2, 3])

        response = self.checkout(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._partial_update(
            pk='current', token=token, props={'item_variant_ids': [1, 2]}
        )

        response = self._delete(pk='current', token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self._get(pk='current', token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('state')['needs_checkout'])

class TestRegisterWithCart(BaseCartTest):

    def register_user(self, props):
        return self.client.post('/api/users/', props)

    def test_passing_cart_to_register_form(self):
        cart = self.get_cart(item_variants=[1, 2])

        user_props = {
            'username': 'username1',
            'email': 'username1@ameba.cat',
            'password': 'mypassword',
            'cart_id': str(cart.id)
        }

        response = self.register_user(props=user_props)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        cart.refresh_from_db()
        self.assertTrue(cart.user)
