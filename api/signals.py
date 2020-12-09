from api.groups import create_group_permissions
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

from api import models
from api.groups import DEFAULT_GROUP


@receiver(signal=post_migrate)
def populate_models(sender, **kwargs):
    create_group_permissions()


@receiver(post_save, sender=models.User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name=DEFAULT_GROUP))
