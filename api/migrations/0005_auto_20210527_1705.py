# Generated by Django 3.1.6 on 2021-05-27 17:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_cover'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(max_length=1000)),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='acquired_items', to=settings.AUTH_USER_MODEL)),
                ('images', models.ManyToManyField(to='api.Image')),
                ('saved_by', models.ManyToManyField(blank=True, related_name='saved_items', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ItemAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='ItemAttributeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='ItemVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('attributes', models.ManyToManyField(to='api.ItemAttribute')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='api.item')),
            ],
        ),
        migrations.AddField(
            model_name='itemattribute',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.itemattributetype'),
        ),
    ]
