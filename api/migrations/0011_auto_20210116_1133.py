# Generated by Django 3.1.5 on 2021-01-16 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='articlevariant',
            old_name='image',
            new_name='images',
        ),
    ]
