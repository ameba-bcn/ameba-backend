from django.db import models
from django.conf import settings


def default_mailing_lists():
    return Subscriber.mailing_lists.through.objects.filter(
        address=settings.DEFAULT_MAILING_LIST
    )


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    mailing_lists = models.ManyToManyField(
        to='MailingList',
        related_name='subscribers',
        default=default_mailing_lists
    )
    created = models.DateTimeField(auto_now_add=True)
