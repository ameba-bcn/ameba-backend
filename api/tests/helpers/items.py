import random
from datetime import datetime

from api import models as api_models
from django.contrib.auth.models import Group


def create_attributes(item_variant):
    color = api_models.ItemAttributeType.objects.create(name='color')
    size = api_models.ItemAttributeType.objects.create(name='size')
    for att, value in (
        (color, 'red'), (size, 'm'), (color, 'green'), (size, 'l')
    ):
        attribute = api_models.ItemAttribute.objects.create(
            attribute=att, value=value
        )
        item_variant.attributes.add(attribute)


def create_item(name, item_class=api_models.Article, is_active=True, pk=None):
    attrs = dict(
        name=name,
        description=f'This is the item {name} with pk {pk}',
        is_active=is_active
    )
    if pk:
        attrs['id'] = pk

    if item_class is api_models.Subscription:
        groups = Group.objects.filter(name=name)
        if groups:
            group = groups.first()
        else:
            max_id = Group.objects.all().order_by('-id')[0].id
            group = Group.objects.create(name=name, pk=max_id + 1)
        attrs['group'] = group
    elif item_class is api_models.Event:
        attrs['datetime'] = datetime.now()
        attrs['address'] = 'Address of the event to go go go and dance dance'

    return item_class.objects.create(**attrs)


def get_item_variant_recurrence(item):
    if item.is_subscription():
        return 'year'
    return None


def get_item_variant_stock(item):
    if item.is_event():
        return random.choice([-1, 30, 100])
    return random.randint(0, 10)


def create_item_variant(item, price=None, stock=None, recurrence=None, pk=None):
    item_variant_data = dict(
        item=item,
        price=price or item.pk * 10,
        stock=stock or get_item_variant_stock(item),
        recurrence=recurrence or get_item_variant_recurrence(item)
    )
    if pk:
        item_variant_data['id'] = pk

    item_variant = api_models.ItemVariant.objects.create(**item_variant_data)
    create_attributes(item_variant)
    return item_variant


def create_items_variants(item_variants, for_free=False,
                          item_class=api_models.Item):
    if item_variants:
        item = create_item(pk=item_variants[0], name=item_variants[0],
                           item_class=item_class, is_active=True)

        for item_variant in item_variants:
            yield create_item_variant(
                item=item,
                price=0 if for_free else item_variant * 10,
                stock=item_variant,
                pk=item_variant
            )
