from unittest import mock
from rest_framework import status

from api.tests.user import BaseUserTest
from api.tests.cart import BaseCartTest
from api.models import Member, User, Subscription
from api import email_factories


class FullRegistrationTest(BaseUserTest):
    LIST_ENDPOINT = '/api/member_register/'

    @mock.patch.object(email_factories.UserRegisteredEmail, 'send_to')
    def test_register_new_user_and_member(self, send_to):
        base_cart_test = BaseCartTest()
        cart = base_cart_test.get_cart(item_variants=[1],
                                       item_class=Subscription)

        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11@ameba.cat',
            'identity_card': '12345678A',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816',
            'cart_id': cart.id
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(email='user11@ameba.cat'))

        user = User.objects.get(email='user11@ameba.cat')
        self.assertTrue(Member.objects.filter(user=user))
        send_to.assert_called()

    @mock.patch.object(email_factories.UserRegisteredEmail, 'send_to')
    def test_register_member_wrong_identity_card(self, send_to):
        base_cart_test = BaseCartTest()
        cart = base_cart_test.get_cart(item_variants=[1],
                                       item_class=Subscription)

        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11@ameba.cat',
            'identity_card': 'A1234',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816',
            'cart_id': cart.id
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch.object(email_factories.UserRegisteredEmail, 'send_to')
    def test_register_new_user_and_member_no_subscription(self, send_to):
        base_cart_test = BaseCartTest()
        cart = base_cart_test.get_cart(item_variants=[1])

        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11@ameba.cat',
            'address': 'My user address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816',
            'cart_id': cart.id
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch.object(email_factories.UserRegisteredEmail, 'send_to')
    def test_register_new_user_and_member_no_cart_id(self, send_to):
        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11@ameba.cat',
            'address': 'My user address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816'
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_new_user_and_member_no_username(self):
        base_cart_test = BaseCartTest()
        cart = base_cart_test.get_cart(item_variants=[1],
                                       item_class=Subscription)

        form_props = {
            'password': 'ameba12345',
            'email': 'user11@ameba.cat',
            'address': 'My user address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816',
            'cart_id': cart.id
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_new_user_and_member_no_wrong_email(self):
        base_cart_test = BaseCartTest()
        cart = base_cart_test.get_cart(item_variants=[1],
                                       item_class=Subscription)

        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11',
            'address': 'My user address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816',
            'cart_id': cart.id
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_new_user_and_member_no_first_name(self):
        base_cart_test = BaseCartTest()
        cart = base_cart_test.get_cart(item_variants=[1],
                                       item_class=Subscription)

        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11',
            'address': 'My user address',
            'last_name': 'Last Name',
            'phone_number': '661839816',
            'cart_id': cart.id
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_email_already_exists(self):
        base_cart_test = BaseCartTest()
        cart = base_cart_test.get_cart(item_variants=[1],
                                       item_class=Subscription)

        self._insert_user(dict(
            username='username',
            email='user11@ameba.cat',
            password='ameba12345'
        ))
        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11@ameba.cat',
            'address': 'My user address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816',
            'cart_id': cart.id
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
