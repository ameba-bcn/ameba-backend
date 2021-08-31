from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from datetime import datetime

from api.models import User, ItemAttributeType, ItemAttribute, Item, \
    Subscription, ItemVariant, Cart, Event


user_types = {
    'web_user': None,
    'ameba_member': None
}


def get_user(username, email, password, group_name='web_user', active=True):
    user = User.objects.create(username=username, email=email,
                               password=password)
    user.is_active = active
    user.save()
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    return user


def get_user_token(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


def create_attributes(item_variant):
    color = ItemAttributeType.objects.create(name='color')
    size = ItemAttributeType.objects.create(name='size')
    for att, value in (
        (color, 'red'), (size, 'm'), (color, 'green'), (size, 'l')
    ):
        attribute = ItemAttribute.objects.create(attribute=att,
                                                 value=value)
        item_variant.attributes.add(attribute)


def create_items_variants(item_variants, for_free=False, item_class=Item):
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
        elif item_class is Event:
            attrs['datetime'] = datetime.now()
            attrs['address'] = 'Bla bla bla bla bla'

        item = item_class.objects.create(**attrs)
        for item_variant in item_variants:
            cart_data = dict(
                id=item_variant,
                item=item,
                price=0 if for_free else item_variant * 10,
                stock=item_variant
            )
            item_variant = ItemVariant.objects.create(**cart_data)
            create_attributes(item_variant)
            yield item_variant


def get_cart(user=None, item_variants=None, for_free=False,
             item_class=Item):
    cart = Cart.objects.create(user=user)
    if item_variants:
        create_items_variants(item_variants, for_free=for_free,
                              item_class=item_class)
        cart.item_variants.set(item_variants)
    return cart
