# Generated by Django 3.1.6 on 2021-08-09 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20210809_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemattributetype',
            name='name_ca_es',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='itemattributetype',
            name='name_en_es',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='itemattributetype',
            name='name_es_es',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
