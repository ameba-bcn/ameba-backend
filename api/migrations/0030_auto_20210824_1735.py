# Generated by Django 3.1.6 on 2021-08-24 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20210824_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='artisttag',
            name='name_ca',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='artisttag',
            name='name_en',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='artisttag',
            name='name_es',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
