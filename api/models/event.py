from datetime import timedelta

from django.utils import timezone
from django.db.models import CharField, DateTimeField, ManyToManyField

from api.models import Item


EXPIRE_HOURS_BEFORE_EVENT = 1
EXPIRE_BEFORE_EVENT = timedelta(hours=EXPIRE_HOURS_BEFORE_EVENT)


class Event(Item):
    datetime = DateTimeField()
    address = CharField(max_length=255)
    artists = ManyToManyField(to='Artist', related_name='events', blank=True)

    def expire(self):
        self.is_active = False
        self.save()

    def get_is_active(self):
        self.is_active = timezone.now() > self.datetime - EXPIRE_BEFORE_EVENT
        return self.is_active
