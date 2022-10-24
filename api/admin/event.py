from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from api.admin.item import BaseItemAdmin
from api.models import Event, EventType


class EventTypeAdmin(TranslationAdmin):
    fields = ('name', )
    list_display = ('name', )


class EventAdmin(BaseItemAdmin):
    fields = ['header'] + BaseItemAdmin.fields + ['datetime', 'address', 'artists', 'type']
    readonly_fields = BaseItemAdmin.readonly_fields + ['participants']
    list_display = BaseItemAdmin.list_display[:3] + ['participants'] + BaseItemAdmin.list_display[3:]

    @staticmethod
    def participants(obj):
        tot = 0
        for iv in obj.variants.all():
            tot += len(iv.acquired_by.all())
        return tot


admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
