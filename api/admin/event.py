from django.contrib import admin
from api.models import Event, Item


class ItemInLine(admin.StackedInline):
    model = Item
    verbose_name = 'Data'
    verbose_name_plural = "Event data"
    insert_before = 'datetime'
    fields = ('name', 'description', 'price', 'stock')


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['datetime', 'address', 'attendees',
                              'interested', 'created', 'updated']})
    ]
    readonly_fields = ['created', 'updated']
    list_display = ['name', 'price', 'datetime', 'address']
    inlines = (ItemInLine,)

    change_form_template = 'admin/custom/change_form.html'

    @staticmethod
    def price(obj):
        return obj.item.price


admin.site.register(Event, EventAdmin)

