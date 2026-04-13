from django.db import migrations
from django.utils import timezone

# Use a high explicit ID to avoid collisions with test fixtures that use
# small integer IDs (1–10). This value is well outside the range tests use.
DELIVERY_FEE_ITEM_ID = 999998
DELIVERY_FEE_VARIANT_ID = 999998


def create_delivery_fee_item(apps, schema_editor):
    Item = apps.get_model('api', 'Item')
    ItemVariant = apps.get_model('api', 'ItemVariant')

    item = Item.objects.create(
        id=DELIVERY_FEE_ITEM_ID,
        name='Delivery Fee',
        description='Home delivery surcharge',
        is_active=True,
        order=timezone.now(),
    )

    ItemVariant.objects.create(
        id=DELIVERY_FEE_VARIANT_ID,
        item=item,
        price=4.00,
        stock=-1,
        is_delivery_fee=True,
    )


def delete_delivery_fee_item(apps, schema_editor):
    Item = apps.get_model('api', 'Item')
    Item.objects.filter(id=DELIVERY_FEE_ITEM_ID).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0082_cart_shipping'),
    ]

    operations = [
        migrations.RunPython(create_delivery_fee_item, delete_delivery_fee_item),
    ]
