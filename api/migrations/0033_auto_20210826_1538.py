# Generated by Django 3.1.6 on 2021-08-26 15:38

import api.models.user
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_auto_20210825_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='member', to=settings.AUTH_USER_MODEL, verbose_name='usuario'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=api.models.user.LowerCaseEmail(max_length=254, unique=True, verbose_name='email'),
        ),
    ]
