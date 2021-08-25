from django.utils.translation import gettext as _
from django.db import models
from django.conf import settings


def default_mailing_lists():
    return Subscriber.mailing_lists.through.objects.filter(
        address=settings.DEFAULT_MAILING_LIST
    )


class Subscriber(models.Model):
    class Meta:
        verbose_name = _('Subscriber')
        verbose_name_plural = _('Subscribers')

    email = models.EmailField(unique=True, verbose_name=_('email'))
    mailing_lists = models.ManyToManyField(
        to='MailingList',
        related_name='subscribers',
        default=default_mailing_lists,
        verbose_name=_('mailing lists')
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created')
    )

    def __str__(self):
        return self.email
