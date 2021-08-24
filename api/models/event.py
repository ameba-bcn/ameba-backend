from datetime import timedelta

from django.utils import timezone
from django.db.models import (
    CharField, DateTimeField, ManyToManyField, Model, ForeignKey, CASCADE
)

from api.models import Item


EXPIRE_HOURS_BEFORE_EVENT = 1
EXPIRE_BEFORE_EVENT = timedelta(hours=EXPIRE_HOURS_BEFORE_EVENT)


class EventType(Model):
    name = CharField(max_length=20, blank=False)

    def __str__(self):
        return f"{self.name}"


class Event(Item):
    datetime = DateTimeField()
    address = CharField(max_length=255)
    type = ForeignKey(to="EventType", on_delete=CASCADE, blank=True, null=True)
    artists = ManyToManyField(to='Artist', related_name='events', blank=True)

    def expire(self):
        self.is_active = False
        self.save()

    def get_is_active(self):
        self.is_active = timezone.now() > self.datetime - EXPIRE_BEFORE_EVENT
        return self.is_active
