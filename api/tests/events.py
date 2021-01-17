from django.utils import timezone
from django.core.files.images import ImageFile
from rest_framework import status
from django.test import tag
from django.contrib.auth.models import Group

from api.tests._helpers import BaseTest, check_structure
from api.tests.user import BaseUserTest
from api.models import Article, ArticleVariant, Image
from api.models import Event, User, Image, Item


class TestSavedUserEvents(BaseTest):
    LIST_ENDPOINT = '/api/users/current/events/saved/'
    DETAIL_ENDPOINT = '/api/users/current/events/saved/{pk}/'

    def setUp(self):
        self.populate_data()

    @staticmethod
    def get_event_data(num):
        event_data_template = {
            'name': 'Event {num}',
            'description': 'Event {num} description',
            'price': '{num}.50',
            'stock': 5,
            'datetime': timezone.now(),
            'address': 'Carrer del Chanquete 3, Barcelona'
        }
        event_data = {}
        for key, value in event_data_template.items():
            if type(value) is str and '{num}' in value:
                event_data[key] = value.format(num=num)
            else:
                event_data[key] = value
        return event_data

    def populate_data(self):
        for i in range(10):
            event_data = self.get_event_data(i)
            event = Event.objects.create(**event_data)
            event.images.add(Image.objects.create(image=ImageFile(
                open('api/tests/fixtures/media/item-image.jpg', 'rb')
            )))

    def test_user_saved_events_list(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        for event in Event.objects.all():
            event.saved_by.add(user)
        response = self._list(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_structure = [{'event': int}]
        self.assertTrue(check_structure(response.data, response_structure))

    def test_user_save_event(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event = Event.objects.all()[0]
        response = self._create(props={'event': event.id}, token=token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_structure = {'event': int}
        self.assertTrue(check_structure(response.data, response_structure))
        self.assertIn(user, event.saved_by.all())

    def test_user_delete_saved_event(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event = Event.objects.all()[0]
        event.saved_by.add(user)
        response = self._delete(pk=event.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_saved_events_list_unauthenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        for event in Event.objects.all():
            event.saved_by.add(user)
        response = self._list()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_save_event_unauthenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event = Event.objects.all()[0]
        response = self._create(props={'event': event.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_delete_saved_event_unauthenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event = Event.objects.all()[0]
        event.saved_by.add(user)
        response = self._delete(pk=event.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_save_non_existent_event(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        response = self._create(props={'event': 99}, token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_delete_non_existent_saved_event(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        response = self._delete(pk=99, token=token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_save_item_not_event(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        item_data = {
            'name': 'Item (note event)',
            'description': 'Item description',
            'price': '10.50',
            'stock': 5
        }
        event = Item.objects.create(**item_data)
        response = self._create(props={'event': event.id}, token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_delete_saved_item_not_event(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        item_data = {
            'name': 'Item (note event)',
            'description': 'Item description',
            'price': '10.50',
            'stock': 5
        }
        event = Item.objects.create(**item_data)
        response = self._delete(pk=event.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
