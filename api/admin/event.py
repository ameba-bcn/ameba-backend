from django.contrib import admin

from api.admin.item import BaseItemAdmin
from api.models import Event


class EventAdmin(BaseItemAdmin):
    fields = BaseItemAdmin.fields + ['datetime', 'address', 'artists']


admin.site.register(Event, EventAdmin)
