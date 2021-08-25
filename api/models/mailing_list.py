from django.db import models
from django.db import DataError
from django.conf import settings
from django.utils.translation import gettext as _


class DeletionNotAllowed(DataError):
    pass


class MailingList(models.Model):
    class Meta:
        verbose_name = _('Mailing list')
        verbose_name_plural = _('Mailing lists')

    address = models.CharField(
        max_length=120, unique=True, verbose_name=_('address')
    )
    is_test = models.BooleanField(default=True, verbose_name=_('is test'))

    def delete(self, using=None, keep_parents=False):
        if self.address == settings.DEFAULT_MAILING_LIST:
            raise DeletionNotAllowed
        return super().delete(using, keep_parents)

    def __str__(self):
        return self.address
