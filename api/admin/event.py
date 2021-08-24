from django.contrib import admin

from api.admin.item import BaseItemAdmin
from api.models import Event


from api.models import Event, EventTag


class EventTagAdmin(admin.ModelAdmin):
    fields = ['name']


class EventAdmin(BaseItemAdmin):
    fields = BaseItemAdmin.fields + ['datetime', 'address', 'artists', 'tag']


admin.site.register(Event, EventAdmin)
admin.site.register(EventTag, EventTagAdmin)
