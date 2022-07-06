from django.utils import timezone
from django.core.files.images import ImageFile
from django.test import tag
from django.contrib.auth.models import Group

from api.tests._helpers import BaseTest, check_structure
from api.models import Image, ItemAttributeType, ItemAttribute, \
    ItemVariant, Subscription


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
        'name': 'Article {num}',
        'description': 'Description for article {num}',
        'benefits': 'Benefits bla bla bla',
        'group': Group.objects.first(),
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


class TestSubscription(BaseTest):
    DETAIL_ENDPOINT = '/api/subscriptions/{pk}/'
    LIST_ENDPOINT = '/api/subscriptions/'

    def setUp(self):
        self.populate_data()

    @staticmethod
    def populate_data():
        for i in range(1, 20):
            item_data = ItemMethods.get_structure(num=i)
            subscription = Subscription.objects.create(**item_data)

            for i in range(i % 4):
                subscription.images.add(Image.objects.create(image=ImageFile(
                    open('api/tests/fixtures/media/item-image.jpg', 'rb')
                )))

            for i in range(i % 4):
                attribute_type = ItemAttributeType.objects.create(
                    name=f'attribute_{i}'
                )
                attribute = ItemAttribute.objects.create(
                    attribute=attribute_type, value=f'value_{i}'
                )
                item_variant = ItemVariant.objects.create(
                    item=subscription, stock=i, price=i
                )
                item_variant.attributes.add(attribute)

    @tag('subscription')
    def test_item_list_has_proper_structure(self):
        structure = [
            {
                'id': int,
                'name': str,
                'images': [str],
                'discount': int,
                'price_range': str,
                'description': str,
                'benefits': str
            }
        ]

        response = self._list(token=None)
        self.assertTrue(check_structure(response.data, structure))

    @tag('subscription')
    def test_item_detail_has_proper_structure(self):
        structure = {
            'id': int,
            'name': str,
            'description': str,
            'benefits': str,
            'discount': int,
            'price_range': str,
            'variants': [{
                'attributes': dict,
                'stock': int,
                'price': str
            }],
            'images': [str],
            'has_stock': bool
        }
        articles = self._list(token=None).data
        for article in articles:
            pk = article['id']
            response = self._get(pk=pk, token=None)
            self.assertTrue(
                check_structure(response.data, structure),
                msg=f'Error on article with pk {pk}'
            )
