# Generated by Django 3.1.5 on 2021-01-16 11:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, unique=True)),
                ('description', models.TextField(max_length=1000)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('stock', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='acquired_items', to=settings.AUTH_USER_MODEL)),
                ('images', models.ManyToManyField(to='api.Image')),
                ('saved_by', models.ManyToManyField(blank=True, related_name='saved_items', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
