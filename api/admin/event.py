from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from api.admin.item import BaseItemAdmin
from api.models import Event, EventType


class EventTypeAdmin(TranslationAdmin):
    fields = ('name', )
    list_display = ('name', )


class EventAdmin(BaseItemAdmin):
    fields = ['header'] + BaseItemAdmin.fields + ['datetime', 'address', 'artists', 'type']


admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
