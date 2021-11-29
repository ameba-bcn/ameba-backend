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


def create_item(pk, name, item_class, is_active=True):
    attrs = dict(
        id=pk,
        name=name,
        description=f'This is the item {name} with pk {pk}',
        is_active=is_active
    )
    if item_class is api_models.Subscription:
        group, created = Group.objects.get_or_create(
            name='ameba_member'
        )
        attrs['group'] = group
    elif item_class is api_models.Event:
        attrs['datetime'] = datetime.now()
        attrs['address'] = 'Address of the event to go go go and dance dance'

    return item_class.objects.create(**attrs)


def create_items_variants(item_variants, for_free=False,
                          item_class=api_models.Item):
    if item_variants:
        item = create_item(pk=item_variants[0], name=item_variants[0],
                           item_class=item_class, )
        for item_variant in item_variants:
            cart_data = dict(
                id=item_variant,
                item=item,
                price=0 if for_free else item_variant * 10,
                stock=item_variant
            )
            item_variant = api_models.ItemVariant.objects.create(**cart_data)
            create_attributes(item_variant)
            yield item_variant
