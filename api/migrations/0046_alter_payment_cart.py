# Generated by Django 3.2 on 2021-12-15 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0045_auto_20211212_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='cart',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payment', to='api.cart'),
        ),
    ]
