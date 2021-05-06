from rest_framework import status

from api.tests.user import BaseUserTest
from api.models import Member, User


class FullRegistrationTest(BaseUserTest):
    LIST_ENDPOINT = '/api/full_registration/'

    def test_register_new_user_and_member(self):
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(email='user11@ameba.cat'))

        user = User.objects.get(email='user11@ameba.cat')
        self.assertTrue(Member.objects.filter(user=user))

    def test_register_new_user_and_member_no_username(self):
        form_props = {
            'password': 'ameba12345',
            'email': 'user11@ameba.cat',
            'address': 'My user address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816'
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_new_user_and_member_no_wrong_email(self):
        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11',
            'address': 'My user address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': '661839816'
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_new_user_and_member_no_first_name(self):
        form_props = {
            'username': 'User2',
            'password': 'ameba12345',
            'email': 'user11',
            'address': 'My user address',
            'last_name': 'Last Name',
            'phone_number': '661839816'
        }

        response = self._create(props=form_props)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
