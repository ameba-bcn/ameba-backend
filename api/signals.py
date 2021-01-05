from api.groups import create_group_permissions
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group

from api import models
from api.groups import DEFAULT_GROUP, MEMBER_GROUP


def populate_models(sender, **kwargs):
    create_group_permissions()


@receiver(post_save, sender=models.User)
def add_user_groups(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name=DEFAULT_GROUP))
        if instance.is_member():
            instance.groups.add(Group.objects.get(name=MEMBER_GROUP))


@receiver(post_save, sender=models.Member)
def on_new_member(sender, instance, created, **kwargs):
    if created and instance.is_user():
        instance.user.groups.add(Group.objects.get(name=MEMBER_GROUP))
