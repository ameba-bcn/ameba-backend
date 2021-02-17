from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(pre_save, sender=get_user_model())
def on_new_user(sender, instance, **kwargs):
    if instance.is_superuser and not instance.is_active:
        instance.is_active = True
