from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0080_alter_member_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemvariant',
            name='is_delivery_fee',
            field=models.BooleanField(default=False, verbose_name='is delivery fee'),
        ),
    ]
