from django.utils import timezone
from django.core.files.images import ImageFile
from rest_framework import status
from django.test import tag
from django.contrib.auth.models import Group

from api.tests._helpers import BaseTest, check_structure
from api.tests.user import BaseUserTest
from api.models import Article, Image
from api.models import Event, User, Image, Item, ItemAttributeType, \
    ItemVariant, ItemAttribute
import api.tests.helpers.items as item_helpers


class BaseEventTest(BaseTest):
    def setUp(self):
        self.populate_data()

    @staticmethod
    def get_event_data(num):
        event_data_template = {
            'name': 'Event {num}',
            'description': 'Event {num} description',
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
        attribute = ItemAttributeType.objects.create(name='size')
        item_attribute = ItemAttribute.objects.create(
            attribute=attribute, value='unique'
        )

        for i in range(10):
            event_data = self.get_event_data(i)
            event = Event.objects.create(**event_data)
            event.images.add(Image.objects.create(image=ImageFile(
                open('api/tests/fixtures/media/item-image.jpg', 'rb')
            )))
            variant = ItemVariant.objects.create(
                item=event, stock=-1, price='15.50'
            )
            variant.attributes.add(item_attribute)
            event.variants.add(variant)


class TestSavedUserEvents(BaseEventTest):
    LIST_ENDPOINT = '/api/users/current/events/saved/'
    DETAIL_ENDPOINT = '/api/users/current/events/saved/{pk}/'

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
            'description': 'Item description'
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
            'description': 'Item description'
        }
        event = Item.objects.create(**item_data)
        response = self._delete(pk=event.id, token=token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestEvents(BaseEventTest):
    LIST_ENDPOINT = '/api/events/'
    DETAIL_ENDPOINT = '/api/events/{pk}/'

    @tag('event')
    def test_events_list_has_proper_structure(self):
        structure = [
            {
                'id': int,
                'name': str,
                'header': str,
                'images': [str],
                'discount': int,
                'saved': bool,
                'purchased': bool
            }
        ]

        response = self._list(token=None)
        self.assertTrue(check_structure(response.data, structure))

    @tag('event')
    def test_events_detail_has_proper_structure(self):
        structure = {
            'id': int,
            'name': str,
            'header': str,
            'description': str,
            'saved': bool,
            'purchased': bool,
            'images': [str],
            'address': str,
            'datetime': str
        }
        items = self._list(token=None).data
        for item in items:
            pk = item['id']
            response = self._get(pk=pk, token=None)
            self.assertTrue(
                check_structure(response.data, structure),
                msg=f'Error on item with pk {pk}'
            )

    @tag('event')
    def test_event_list_not_saved_events_not_authenticated(self):
        response = self._list(token=None)
        for event in response.data:
            self.assertFalse(event['saved'])

    @tag('event')
    def test_event_list_not_saved_events_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        response = self._list(token=token)
        for event in response.data:
            self.assertFalse(event['saved'])

    @tag('event')
    def test_event_list_saved_event_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event_obj = Event.objects.all()[0]
        event_obj.saved_by.add(user)
        response = self._list(token=token)
        for event in response.data:
            if event['id'] == event_obj.id:
                self.assertTrue(event['saved'])
            else:
                self.assertFalse(event['saved'])

    @tag('event')
    def test_event_list_saved_event_not_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event_obj = Event.objects.all()[0]
        event_obj.saved_by.add(user)
        response = self._list(token=None)
        for event in response.data:
            self.assertFalse(event['saved'])

    @tag('event')
    def test_event_list_not_purchased_events_not_authenticated(self):
        response = self._list(token=None)
        for event in response.data:
            self.assertFalse(event['saved'])

    @tag('event')
    def test_event_list_not_purchased_events_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        response = self._list(token=token)
        for event in response.data:
            self.assertFalse(event['purchased'])

    @tag('event')
    def test_event_list_purchased_event_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event_obj = item_helpers.create_item(name='Event', item_class=Event)
        event_variant = item_helpers.create_item_variant(item=event_obj)
        event_variant.acquired_by.add(user)
        response = self._list(token=token)
        for event in response.data:
            if event['id'] == event_obj.id:
                self.assertTrue(event['purchased'])
            else:
                self.assertFalse(event['purchased'])

    @tag('event')
    def test_event_list_purchased_events_not_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event_obj = item_helpers.create_item(name='Event', item_class=Event)
        event_variant = item_helpers.create_item_variant(item=event_obj)
        event_variant.acquired_by.add(user)
        response = self._list(token=None)
        for event in response.data:
            self.assertFalse(event['purchased'])

    @tag('event')
    def test_event_list_purchased_events_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event_obj = item_helpers.create_item(name='Event', item_class=Event)
        event_variant = item_helpers.create_item_variant(item=event_obj)
        event_variant.acquired_by.add(user)
        response = self._list(token=token)
        for event in response.data:
            if event['id'] == event_obj.id:
                self.assertTrue(event['purchased'])
            else:
                self.assertFalse(event['purchased'])

    @tag('event')
    def test_event_list_purchased_item_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        item_obj = item_helpers.create_item(name='Item', item_class=Item)
        item_variant = item_helpers.create_item_variant(item=item_obj)
        item_variant.acquired_by.add(user)
        response = self._list(token=token)
        for event in response.data:
            self.assertFalse(event['purchased'])

    @tag('event')
    def test_event_list_saved_item_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        item_data = {
            'name': 'Item (note event)',
            'description': 'Item description'
        }
        event_obj = Item.objects.create(**item_data)
        event_obj.saved_by.add(user)
        response = self._list(token=token)
        for event in response.data:
            self.assertFalse(event['saved'])


class TestEventTicket(BaseEventTest):
    LIST_ENDPOINT = '/api/ticket/'

    def test_event_token_can_access_event_user_info(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event_obj = Event.objects.all()[0]
        variant = event_obj.variants.all()[0]
        variant.acquired_by.add(user)

        token = user.get_event_token(variant.pk)
        response = self._list(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_wrong_token_can_not_access_event_user_info(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        event_obj = Event.objects.all()[0]
        variant = event_obj.variants.all()[0]
        variant.acquired_by.add(user)

        token = user.get_event_token(variant.pk)[:-1]
        response = self._list(token=token)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
