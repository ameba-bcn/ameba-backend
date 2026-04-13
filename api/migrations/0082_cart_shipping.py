from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0081_itemvariant_is_delivery_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='shipping',
            field=models.JSONField(blank=True, null=True, verbose_name='shipping'),
        ),
    ]
