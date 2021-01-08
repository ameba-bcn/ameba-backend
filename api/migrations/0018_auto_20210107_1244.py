# Generated by Django 3.1.5 on 2021-01-07 12:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20210107_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cart',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
