# Generated by Django 3.1.6 on 2021-05-27 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('api', '0005_auto_20210527_1705'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.item')),
                ('benefits', models.TextField(default='', max_length=1000)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='auth.group')),
            ],
            bases=('api.item',),
        ),
    ]
