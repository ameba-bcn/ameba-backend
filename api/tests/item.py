from django.utils import timezone
from django.core.files.images import ImageFile
from rest_framework import status
from django.test import tag
from django.contrib.auth.models import Group

from api.tests._helpers import BaseTest, check_structure
from api.tests.user import BaseUserTest
from api.models import Image, Item
from api.models import Discount


class ModelMethods:
    structure = {}

    @classmethod
    def get_structure(cls, num):
        struct = {}
        for key, value in cls.structure.items():
            if value is None and hasattr(cls, f'get_{key}'):
                value = getattr(cls, f'get_{key}')(num)
            elif type(value) is str:
                value = value.format(num=num)
            struct[key] = value
        return struct


class ItemMethods(ModelMethods):
    structure = {
        'name': 'Item {num}',
        'description': 'Description for item {num}',
        'price': 25,
        'stock': 10,
        'is_active': None
    }

    @staticmethod
    def get_price(num):
        return num

    @staticmethod
    def get_is_active(num):
        return num % 4 == 0

    @staticmethod
    def get_date(num):
        return timezone.now()


class ItemSizeMethods(ModelMethods):
    structure = {
        'size': '{num}',
        'genre': None,
        'stock': None
    }

    @staticmethod
    def get_stock(num):
        return num

    @staticmethod
    def get_genre(num):
        return ['unisex', 'women', 'men'][num % 3]


class TestItem(BaseTest):
    DETAIL_ENDPOINT = '/api/items/{pk}/'
    LIST_ENDPOINT = '/api/items/'

    def setUp(self):
        self.populate_data()

    @staticmethod
    def populate_data():
        for i in range(1, 20):
            item_data = ItemMethods.get_structure(num=i)
            item = Item.objects.create(**item_data)

            for i in range(i % 4):
                item.images.add(Image.objects.create(image=ImageFile(
                        open('api/tests/fixtures/media/item-image.jpg', 'rb')
                    )))

            for i in range(i % 4):
                item_size_data = ItemSizeMethods.get_structure(i)
                item_size_data['item'] = item
                av = ItemSize.objects.create(**item_size_data)
                item.attributes.add(av)

    @tag('item')
    def test_item_list_has_proper_structure(self):
        structure = [
            {
                'id': int,
                'name': str,
                'price': str,
                'images': [str],
                'discount': str
            }
        ]

        response = self._list(token=None)
        self.assertTrue(check_structure(response.data, structure))

    @tag('item')
    def test_item_detail_has_proper_structure(self):
        structure = {
            'id': int,
            'name': str,
            'description': str,
            'price': str,
            'stock':    int,
            'variants': [{
                'size': str,
                'genre': int,
                'stock': int
            }],
            'images': [str],
            'is_active': bool,
        }
        items = self._list(token=None).data
        for item in items:
            pk = item['id']
            response = self._get(pk=pk, token=None)
            self.assertTrue(
                check_structure(response.data, structure),
                msg=f'Error on item with pk {pk}'
            )

    @tag('item')
    def test_inactive_items_are_not_listed(self):
        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 25,
            'stock': 10,
            'is_active': True,
        }
        expired_item_data = dict(item_data)
        expired_item_data['is_active'] = False
        expired_item_data['name'] = 'Inactive Item'
        item = Item.objects.create(**item_data)
        expired_item = Item.objects.create(**expired_item_data)

        response = self._list(token=None)
        response_ids = [response_item['id'] for response_item in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(item.id, response_ids)
        self.assertNotIn(expired_item.id, response_ids)

    @tag('item')
    def test_inactive_item_is_no_accessible_by_id(self):
        expired_item_data = {
            'name': 'Expired Item',
            'description': 'Description for item',
            'price': 25,
            'stock': 10,
            'is_active': False,
        }
        expired_item = Item.objects.create(**expired_item_data)

        response = self._get(pk=expired_item.id, token=None)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_group_discount_applied_in_detail_view_authenticated(self):
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)

        ameba_member = Group.objects.get(name='ameba_member')
        ameba_user = Group.objects.get(name='web_user')

        user.groups.add(ameba_user, ameba_member)

        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 100,
            'stock': 10,
            'is_active': True
        }
        item = Item.objects.create(**item_data)

        discount_data = {
            'name': 'members',
            'value': 20,
            'need_code': False,
            'number_of_uses': -1
        }
        discount = Discount.objects.create(**discount_data)
        discount.groups.add(ameba_member)
        item.discounts.add(discount)

        response = self._get(pk=item.pk, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['discount'], "20")

    def test_no_discount_applied_if_not_authenticated(self):
        user_data = {
            'username': 'minolito',
            'email': 'min@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        ameba_member = Group.objects.get(name='ameba_member')
        ameba_user = Group.objects.get(name='web_user')
        user.groups.add(ameba_user, ameba_member)
        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 100,
            'stock': 10,
            'is_active': True
        }
        item = Item.objects.create(**item_data)
        discount_data = {
            'name': 'members',
            'value': 20,
            'need_code': False,
            'number_of_uses': -1
        }
        discount = Discount.objects.create(**discount_data)
        discount.groups.add(ameba_member)
        item.discounts.add(discount)

        response = self._get(pk=item.pk, token=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['discount'], "")

    def test_discount_applied_in_list_for_auth_user(self):
        user_data = {
            'username': 'minolito',
            'email': 'min@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        ameba_member = Group.objects.get(name='ameba_member')
        ameba_user = Group.objects.get(name='web_user')
        user.groups.add(ameba_user, ameba_member)
        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 100,
            'stock': 10,
            'is_active': True
        }
        item = Item.objects.create(**item_data)
        discount_data = {
            'name': 'members',
            'value': 20,
            'need_code': False,
            'number_of_uses': -1
        }
        discount = Discount.objects.create(**discount_data)
        discount.groups.add(ameba_member)
        item.discounts.add(discount)

        response = self._list(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for resp_item in response.data:
            if resp_item['id'] == item.id:
                self.assertEqual(resp_item['discount'], "20")
                break
            else:
                self.assertEqual(resp_item['discount'], "")

    def test_max_discount_is_applied_in_list_when_multiple(self):
        user_data = {
            'username': 'minolito',
            'email': 'min@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        ameba_member = Group.objects.get(name='ameba_member')
        ameba_user = Group.objects.get(name='web_user')
        user.groups.add(ameba_user, ameba_member)
        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 100,
            'stock': 10,
            'is_active': True
        }
        item = Item.objects.create(**item_data)
        discount_1_data = {
            'name': 'members',
            'value': 20,
            'need_code': False,
            'number_of_uses': -1
        }
        discount = Discount.objects.create(**discount_1_data)
        discount.groups.add(ameba_member)
        item.discounts.add(discount)

        discount_2_data = {
            'name': 'members',
            'value': 30,
            'need_code': False,
            'number_of_uses': -1
        }
        discount_2 = Discount.objects.create(**discount_2_data)
        discount_2.groups.add(ameba_member)
        item.discounts.add(discount_2)

        response = self._list(token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for resp_item in response.data:
            if resp_item['id'] == item.id:
                self.assertEqual(resp_item['discount'], "30")
                break
            else:
                self.assertEqual(resp_item['discount'], "")

    def test_max_discount_is_applied_in_detail_when_multiple(self):
        user_data = {
            'username': 'minolito',
            'email': 'min@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        ameba_member = Group.objects.get(name='ameba_member')
        ameba_user = Group.objects.get(name='web_user')
        user.groups.add(ameba_user, ameba_member)
        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 100,
            'stock': 10,
            'is_active': True
        }
        item = Item.objects.create(**item_data)
        discount_1_data = {
            'name': 'members',
            'value': 20,
            'need_code': False,
            'number_of_uses': -1
        }
        discount = Discount.objects.create(**discount_1_data)
        discount.groups.add(ameba_member)
        item.discounts.add(discount)

        discount_2_data = {
            'name': 'members',
            'value': 30,
            'need_code': False,
            'number_of_uses': -1
        }
        discount_2 = Discount.objects.create(**discount_2_data)
        discount_2.groups.add(ameba_member)
        item.discounts.add(discount_2)

        response = self._get(pk=item.pk, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['discount'], "30")

    def test_discount_not_applies_if_no_remaining_usages(self):
        user_data = {
            'username': 'minolito',
            'email': 'min@olito.com',
            'password': 'ameba12345'
        }
        user, token = BaseUserTest._insert_user(user_data)
        ameba_member = Group.objects.get(name='ameba_member')
        ameba_user = Group.objects.get(name='web_user')
        user.groups.add(ameba_user, ameba_member)
        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 100,
            'stock': 10,
            'is_active': True
        }
        item = Item.objects.create(**item_data)
        discount_1_data = {
            'name': 'members',
            'value': 20,
            'need_code': False,
            'number_of_uses': 0
        }
        discount = Discount.objects.create(**discount_1_data)
        discount.groups.add(ameba_member)
        item.discounts.add(discount)

        response = self._get(pk=item.pk, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['discount'], "")

    def test_get_other_items_but_items_not_listed(self):
        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 100,
            'stock': 10,
            'is_active': True
        }
        item = Item.objects.create(**item_data)
        response = self._list(token=None)
        item = Item.objects.filter(is_active=True)[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item_ids = [item['id'] for item in response.data]
        self.assertNotIn(item.id, item_ids)
        self.assertIn(item.id, item_ids)

    def test_get_item_not_item_is_not_found(self):
        item_data = {
            'name': 'Item',
            'description': 'Description for item',
            'price': 100,
            'stock': 10,
            'is_active': True
        }
        item = Item.objects.create(**item_data)
        response = self._get(pk=item.id, token=None)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_stock_is_item_stock_if_there_is_no_sizes(self):
        item = Item.objects.create(**{
            'name': 'Item',
            'description': 'Description for item',
            'price': 25,
            'stock': 5
        })

        response = self._get(pk=item.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock'], 5)

    def test_stock_is_computed_from_sizes_if_there_are_sizes(self):
        item = Item.objects.create(**{
            'name': 'Item',
            'description': 'Description for item',
            'price': 25,
            'stock': 5
        })
        stocks = [2, 4, 6]
        for stock in stocks:
            size = ItemSize.objects.create(**{
                'size': 'm',
                'genre': 'men',
                'stock': stock,
                'item': item
            })
            item.attributes.add(size)

        response = self._get(pk=item.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock'], sum(stocks))

    def test_stock_is_zero_if_computed_from_sizes_is_zero(self):
        item = Item.objects.create(**{
            'name': 'Item',
            'description': 'Description for item',
            'price': 25,
            'stock': 5
        })
        stocks = [0, 0, 0]
        for stock in stocks:
            size = ItemSize.objects.create(**{
                'size': 'm',
                'genre': 'men',
                'stock': stock,
                'item': item
            })
            item.attributes.add(size)

        response = self._get(pk=item.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock'], sum(stocks))
