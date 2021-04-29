# Generated by Django 3.1.6 on 2021-04-27 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_mailinglist_subscriber'),
    ]

    operations = [
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
                ('attributes', models.ManyToManyField(to='api.ItemAttribute')),
            ],
        ),
        migrations.RemoveField(
            model_name='articlesize',
            name='article',
        ),
        migrations.RemoveField(
            model_name='item',
            name='stock',
        ),
        migrations.DeleteModel(
            name='Article',
        ),
        migrations.DeleteModel(
            name='ArticleSize',
        ),
        migrations.AddField(
            model_name='itemvariant',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='api.item'),
        ),
        migrations.AddField(
            model_name='itemattribute',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.itemattributetype'),
        ),
    ]
