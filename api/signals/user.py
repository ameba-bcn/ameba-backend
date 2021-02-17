from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from api.groups import GROUPS, ADMIN_GROUP


@receiver(pre_save, sender=get_user_model())
def pre_save_user(sender, instance, **kwargs):
    if (instance.is_superuser or instance.is_staff) and not instance.is_active:
        instance.is_active = True


@receiver(post_save, sender=get_user_model())
def post_save_user(sender, instance, **kwargs):
    if instance.is_superuser:
        admin_group = Group.objects.get(id=GROUPS[ADMIN_GROUP]['pk'])
        instance.groups.add(admin_group)
