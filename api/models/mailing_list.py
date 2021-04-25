from django.db import models
from django.db import DataError
from django.conf import settings


class DeletionNotAllowed(DataError):
    pass


class MailingList(models.Model):
    address = models.CharField(max_length=120, unique=True)
    is_test = models.BooleanField(default=True)

    def delete(self, using=None, keep_parents=False):
        if self.address == settings.DEFAULT_MAILING_LIST:
            raise DeletionNotAllowed
        return super().delete(using, keep_parents)

    def __str__(self):
        return self.address
