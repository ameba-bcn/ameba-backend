from django.conf import settings
import django.dispatch as dispatch
import django.db.models.signals as signals

from api.models import MailingList, Subscriber, User


@dispatch.receiver(signals.post_save, sender=User)
def on_new_user(sender, instance, created, **kwargs):
    """ Creates new subscriber to default mailing list. """
    if created:
        subscriber = Subscriber.objects.get_or_create(email=instance.email)
        mailing_list = MailingList.objects.get(
            address=settings.DEFAULT_MAILING_LIST
        )
        subscriber.mailing_lists.add(mailing_list)


@dispatch.receiver(signals.pre_delete, sender=User)
def on_deleted_user(sender, instance, created, **kwargs):
    """ Deletes subscriber from mailing lists. """
    if Subscriber.objects.filter(email=instance.email):
        subscriber = Subscriber.objects.get_or_create(email=instance.email)
        subscriber.delete()
