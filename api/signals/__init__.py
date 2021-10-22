from api.groups import create_group_permissions
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from api import models
from api.groups import DEFAULT_GROUP, MEMBER_GROUP
from api.signals.emails import user_registered, new_membership
from api.signals.payments import cart_checkout, cart_processed
from api.signals.user import on_new_user
from api.signals.mailing_lists import create_mailing_lists
from api.signals.subscriber import on_new_user, on_deleted_user
from api.signals.mailgun import on_deleted_subscription, on_new_subscription
from api.signals.items import items_acquired


def populate_models(sender, **kwargs):
    create_group_permissions()
    # create_mailing_lists()


@receiver(post_save, sender=models.User)
def add_user_groups(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name=DEFAULT_GROUP))
        if instance.has_member_profile():
            instance.groups.add(Group.objects.get(name=MEMBER_GROUP))


@receiver(post_save, sender=models.Member)
def on_new_member(sender, instance, created, **kwargs):
    pass
