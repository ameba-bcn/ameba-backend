from datetime import timedelta, datetime
from django.db.models import (
    Model, CharField, DateTimeField, ForeignKey, DO_NOTHING, ManyToManyField,
    BooleanField
)


EXPIRE_HOURS_BEFORE_EVENT = 1
EXPIRE_BEFORE_EVENT = timedelta(hours=EXPIRE_HOURS_BEFORE_EVENT)


class Event(Model):
    name = CharField(max_length=50)
    datetime = DateTimeField()
    address = CharField(max_length=255)
    item = ForeignKey(to='Item', on_delete=DO_NOTHING, related_name='events')
    attendees = ManyToManyField(to='User', related_name='events')
    interested = ManyToManyField(to='User', related_name='remind_events')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    is_closed = BooleanField()

    def close(self):
        self.is_closed = True
        self.save()

    def get_is_closed(self):
        if datetime.now() > self.datetime - EXPIRE_BEFORE_EVENT:
            self.close()
        return self.is_closed
