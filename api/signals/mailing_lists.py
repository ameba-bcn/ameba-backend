from django.conf import settings

from api.models import MailingList


def create_mailing_lists():
    MailingList.objects.get_or_create(address=settings.DEFAULT_MAILING_LIST)
