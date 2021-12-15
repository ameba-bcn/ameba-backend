from django.conf import settings
import django.dispatch as dispatch
import django.db.models.signals as signals

import api.models as api_models


@dispatch.receiver(signals.post_save, sender=api_models.User)
def on_new_user(sender, instance, created, **kwargs):
    """ Creates new subscriber to default mailing list. """
    if created:
        subscriber, created = api_models.Subscriber.objects.get_or_create(
            email=instance.email
        )
        mailing_list, created = api_models.MailingList.objects.get_or_create(
            address=settings.DEFAULT_MAILING_LIST
        )
        subscriber.mailing_lists.add(mailing_list)


@dispatch.receiver(signals.pre_delete, sender=api_models.User)
def on_deleted_user(sender, instance, **kwargs):
    """ Deletes subscriber from mailing lists. """
    if api_models.Subscriber.objects.filter(email=instance.email):
        subscriber = api_models.Subscriber.objects.get(email=instance.email)
        subscriber.delete()
