# Generated by Django 3.1.6 on 2021-04-29 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_auto_20210429_1735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='benefits',
        ),
        migrations.AddField(
            model_name='itemvariant',
            name='benefits',
            field=models.TextField(default='', max_length=1000),
        ),
    ]
