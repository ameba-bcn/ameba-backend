# Generated by Django 3.1.6 on 2021-02-06 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20210206_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkout',
            name='details',
            field=models.JSONField(blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='chart_record',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='payment',
            name='details',
            field=models.JSONField(blank=True),
        ),
    ]
