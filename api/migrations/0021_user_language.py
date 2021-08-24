# Generated by Django 3.1.6 on 2021-08-11 07:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_language_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.language'),
        ),
    ]
