# Generated by Django 3.1.5 on 2021-01-16 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('duration', models.IntegerField(default=365)),
                ('expires', models.DateTimeField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('number', models.IntegerField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('phone_number', models.CharField(max_length=10)),
                ('memberships', models.ManyToManyField(blank=True, to='api.Membership')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
