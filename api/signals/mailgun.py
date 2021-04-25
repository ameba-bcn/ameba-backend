from django.conf import settings
import django.dispatch as dispatch
import django.db.models.signals as signals

from api import mailgun
from api.models import MailingList, Subscriber


@dispatch.receiver(signals.m2m_changed,sender=Subscriber.mailing_lists.through)
def on_new_subscription(instance, pk_set, action, model, **kwargs):
    """ After new entry/ies at m2m intermediate table between Subscriber and
    MailingList: add member in mailgun list to every MailingList added to
    that Subscriber. """
    if action == 'post_add':
        for mailing_list_id in pk_set:
            subscriber = instance
            mailing_list = model.objects.get(pk=mailing_list_id)
            mailing_list_address = mailing_list.address
            email = subscriber.email
            mailgun.add_member(
                email=email, list_address=mailing_list_address
            )


@dispatch.receiver(signals.m2m_changed,sender=Subscriber.mailing_lists.through)
def on_deleted_subscription(instance, action, model, pk_set, *args, **kwargs):
    if action == 'post_remove':
        for mailing_list_id in pk_set:
            subscriber = instance
            mailing_list = model.objects.get(pk=mailing_list_id)
            mailing_list_address = mailing_list.address
            email = subscriber.email
            mailgun.remove_member(
                email=email, list_address=mailing_list_address
            )


@dispatch.receiver(signals.post_save, sender=MailingList)
def on_new_mailing_list(instance, *args, **kwargs):
    mailgun.post_mailing_list(list_address=instance.address)


@dispatch.receiver(signals.pre_delete, sender=MailingList)
def on_delete_mailing_list(instance, *args, **kwargs):
    mailgun.delete_mailing_list(list_address=instance.address)
