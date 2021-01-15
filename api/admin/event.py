from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils.html import mark_safe

from api.models import Event, Item, ItemImage


class ItemInLine(admin.StackedInline):
    model = Item
    verbose_name = 'Data'
    verbose_name_plural = "Event data"
    insert_before = 'datetime'
    fields = ('name', 'description', 'price', 'stock')


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['datetime', 'address', 'image', 'preview',
                           'attendees', 'interested', 'created', 'updated']})
    ]
    readonly_fields = ['created', 'updated', 'preview']
    list_display = ['name', 'price', 'datetime', 'address',
                    'list_attendees', 'list_interested', 'list_preview']
    search_field = ['name']
    inlines = (ItemInLine, )
    change_form_template = 'admin/custom/change_form.html'

    @staticmethod
    def list_attendees(obj):
        return obj.attendees.count()
    list_attendees.short_description = 'Attendees'
    list_attendees.allow_tags = True

    @staticmethod
    def list_interested(obj):
        return obj.interested.count()
    list_interested.short_description = 'Interested'
    list_interested.allow_tags = True

    @staticmethod
    def price(obj):
        return obj.item.price

    @staticmethod
    def preview(obj):
        if obj.image:
            return mark_safe(
                '<img src="{}" width="300" height="300" />'.format(
                    obj.image.url
                ))

    preview.short_description = 'Preview'
    preview.allow_tags = True

    @staticmethod
    def list_preview(obj):
        if obj.image:
            return mark_safe(
                '<img src="{}" width="75" height="75" />'.format(
                    obj.image.url
                ))
    list_preview.short_description = 'List preview'
    list_preview.allow_tags = True



admin.site.register(Event, EventAdmin)
