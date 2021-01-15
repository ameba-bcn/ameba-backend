from datetime import timedelta

from django.utils import timezone
from django.db.models import (
    Model, CharField, DateTimeField, ForeignKey, DO_NOTHING, ManyToManyField,
    BooleanField, TextField, ImageField
)


EXPIRE_HOURS_BEFORE_EVENT = 1
EXPIRE_BEFORE_EVENT = timedelta(hours=EXPIRE_HOURS_BEFORE_EVENT)


class Event(Model):
    datetime = DateTimeField()
    address = CharField(max_length=255)
    image = ImageField(upload_to='events')
    attendees = ManyToManyField(to='User', related_name='events', blank=True)
    interested = ManyToManyField(to='User', related_name='remind_events',
                                 blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    is_closed = BooleanField()

    @property
    def name(self):
        return self.item.name

    @name.setter
    def name(self, value):
        self.item.name = value
        self.item.save()

    @property
    def description(self):
        return self.item.description

    @description.setter
    def description(self, value):
        self.item.description = value
        self.item.save()

    def close(self):
        self.is_closed = True
        self.save()

    def get_is_closed(self):
        return timezone.now() > self.datetime - EXPIRE_BEFORE_EVENT

    def save(self, *args, **kwargs):
        self.is_closed = self.get_is_closed()
        super().save(*args, **kwargs)
