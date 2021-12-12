from datetime import timedelta

from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import (
    CharField, DateTimeField, ManyToManyField, Model, ForeignKey, CASCADE
)

from api.models import Item


EXPIRE_HOURS_BEFORE_EVENT = 1
EXPIRE_BEFORE_EVENT = timedelta(hours=EXPIRE_HOURS_BEFORE_EVENT)


class EventType(Model):
    class Meta:
        verbose_name = _('Event type')
        verbose_name_plural = _('Event types')

    name = CharField(max_length=20, blank=False, verbose_name=_('name'))

    def __str__(self):
        return f"{self.name}"


class Event(Item):
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    datetime = DateTimeField(verbose_name=_('datetime'))
    address = CharField(max_length=255, verbose_name=_('address'))
    type = ForeignKey(
        to="EventType", on_delete=CASCADE, blank=True, null=True,
        verbose_name=_('type')
    )
    artists = ManyToManyField(
        to='Artist', related_name='events', blank=True, verbose_name=_('artists')
    )

    def expire(self):
        self.is_active = False
        self.save()

    def get_is_active(self):
        self.is_active = timezone.now() > self.datetime - EXPIRE_BEFORE_EVENT
        return self.is_active

    @property
    def str_datetime(self):
        return self.datetime.strftime('%d/%m/%Y - %H:%M')
