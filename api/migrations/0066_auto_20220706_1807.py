# Generated by Django 3.2 on 2022-07-06 18:07

import api.models.member
import api.models.subscriber
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0065_alter_item_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'verbose_name': 'Respuesta', 'verbose_name_plural': 'Respuestas'},
        ),
        migrations.AlterModelOptions(
            name='interview',
            options={'verbose_name': 'Entrevista', 'verbose_name_plural': 'Entrevistas'},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'verbose_name': 'Ítem', 'verbose_name_plural': 'Ítems'},
        ),
        migrations.AlterModelOptions(
            name='itemattribute',
            options={'verbose_name': 'Atributo de ítem', 'verbose_name_plural': 'Atributos de ítem'},
        ),
        migrations.AlterModelOptions(
            name='itemattributetype',
            options={'verbose_name': 'Tipo de atributo de ítem', 'verbose_name_plural': 'Tipos de atributos de ítem'},
        ),
        migrations.AlterModelOptions(
            name='itemvariant',
            options={'verbose_name': 'Variante de ítem', 'verbose_name_plural': 'Variantes de ítem'},
        ),
        migrations.AlterModelOptions(
            name='mailinglist',
            options={'verbose_name': 'Lista de emails', 'verbose_name_plural': 'Listas de emails'},
        ),
        migrations.AlterModelOptions(
            name='member',
            options={'verbose_name': 'Socio', 'verbose_name_plural': 'Socios'},
        ),
        migrations.AlterModelOptions(
            name='membership',
            options={'verbose_name': 'Membresía', 'verbose_name_plural': 'Membresías'},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'verbose_name': 'Pago', 'verbose_name_plural': 'Pagos'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'Pregunta', 'verbose_name_plural': 'Preguntas'},
        ),
        migrations.AlterModelOptions(
            name='subscriber',
            options={'verbose_name': 'Subscriptor', 'verbose_name_plural': 'Subscriptores'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Subscripción', 'verbose_name_plural': 'Subscripciones'},
        ),
        migrations.AddField(
            model_name='question',
            name='position',
            field=models.IntegerField(blank=True, default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='answer',
            name='answer',
            field=models.TextField(max_length=5000, verbose_name='respuesta'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='interview',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='api.interview', verbose_name='entrevista'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='activo'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.question', verbose_name='pregunta'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.artist', verbose_name='artista'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='image',
            field=models.ImageField(blank=True, upload_to='interviews', verbose_name='imágen'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='introduction',
            field=models.TextField(blank=True, max_length=5000, verbose_name='introducción'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='introduction_ca',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='introducción'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='introduction_es',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='introducción'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='actualizado en'),
        ),
        migrations.AlterField(
            model_name='item',
            name='images',
            field=models.ManyToManyField(to='api.Image', verbose_name='imágenes'),
        ),
        migrations.AlterField(
            model_name='item',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='activo'),
        ),
        migrations.AlterField(
            model_name='item',
            name='saved_by',
            field=models.ManyToManyField(blank=True, related_name='saved_items', to=settings.AUTH_USER_MODEL, verbose_name='guardado por'),
        ),
        migrations.AlterField(
            model_name='item',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='actualizado en'),
        ),
        migrations.AlterField(
            model_name='itemattribute',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.itemattributetype', verbose_name='atributo'),
        ),
        migrations.AlterField(
            model_name='itemattribute',
            name='value',
            field=models.CharField(max_length=15, verbose_name='valor'),
        ),
        migrations.AlterField(
            model_name='itemvariant',
            name='acquired_by',
            field=models.ManyToManyField(blank=True, related_name='item_variants', to=settings.AUTH_USER_MODEL, verbose_name='adquirido por'),
        ),
        migrations.AlterField(
            model_name='itemvariant',
            name='attributes',
            field=models.ManyToManyField(to='api.ItemAttribute', verbose_name='atributo'),
        ),
        migrations.AlterField(
            model_name='itemvariant',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='api.item', verbose_name='ítem'),
        ),
        migrations.AlterField(
            model_name='itemvariant',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='precio'),
        ),
        migrations.AlterField(
            model_name='mailinglist',
            name='address',
            field=models.CharField(max_length=120, unique=True, verbose_name='dirección'),
        ),
        migrations.AlterField(
            model_name='mailinglist',
            name='is_test',
            field=models.BooleanField(default=True, verbose_name='de prueba'),
        ),
        migrations.AlterField(
            model_name='member',
            name='first_name',
            field=models.CharField(max_length=20, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_name',
            field=models.CharField(max_length=20, verbose_name='Apellidos'),
        ),
        migrations.AlterField(
            model_name='member',
            name='number',
            field=models.IntegerField(default=api.models.member.get_default_number, primary_key=True, serialize=False, verbose_name='número'),
        ),
        migrations.AlterField(
            model_name='member',
            name='phone_number',
            field=models.CharField(max_length=10, verbose_name='número de teléfono'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='duration',
            field=models.IntegerField(default=365, verbose_name='duración'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='expires',
            field=models.DateTimeField(blank=True, verbose_name='caduca'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='api.member', verbose_name='socio'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='starts',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='comienza'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='subscription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='memberships', to='api.subscription', verbose_name='subscripción'),
        ),
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(default='Ronda de Sant Pau, 17, 08015 Barcelona', max_length=1000, verbose_name='dirección'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='cart_record',
            field=models.JSONField(null=True, verbose_name='registro de carrito'),
        ),
        migrations.AlterField(
            model_name='question',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='por defecto'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question',
            field=models.TextField(max_length=2000, verbose_name='pregunta'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='mailing_lists',
            field=models.ManyToManyField(default=api.models.subscriber.default_mailing_lists, related_name='subscribers', to='api.MailingList', verbose_name='listas de emails'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='benefits',
            field=models.TextField(default='', max_length=1000, verbose_name='beneficios'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='benefits_ca',
            field=models.TextField(default='', max_length=1000, null=True, verbose_name='beneficios'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='benefits_es',
            field=models.TextField(default='', max_length=1000, null=True, verbose_name='beneficios'),
        ),
    ]
