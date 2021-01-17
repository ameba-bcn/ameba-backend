from django.contrib import admin
from django.utils.html import mark_safe

from api.models import Event
from api.admin.article import DiscountChoiceInLine


class ImagesInLine(admin.StackedInline):
    model = Event.images.through
    verbose_name = 'Image'
    verbose_name_plural = "Images"
    fields = ('image', 'preview')
    readonly_fields = ('preview', )
    extra = 0

    @staticmethod
    def preview(obj):
        if obj.image:
            return mark_safe(
                '<img src="{}" width="300" height="300" />'.format(
                    obj.image.url
                ))

    preview.short_description = 'Preview'
    preview.allow_tags = True


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'description', 'price', 'stock',
                           'datetime', 'address', 'acquired_by', 'saved_by',
                           'created', 'updated']})
    ]
    readonly_fields = ['created', 'updated']
    list_display = ['name', 'price', 'datetime', 'address', 'list_acquired_by',
                    'list_saved_by', 'list_preview']
    search_fields = ['name']
    inlines = (ImagesInLine, DiscountChoiceInLine)

    @staticmethod
    def list_saved_by(obj):
        return obj.saved_by.count()
    list_saved_by.short_description = 'Saved by'
    list_saved_by.allow_tags = True

    @staticmethod
    def list_acquired_by(obj):
        return obj.acquired_by.count()
    list_acquired_by.short_description = 'Acquired by'
    list_acquired_by.allow_tags = True

    @staticmethod
    def price(obj):
        return obj.item.price

    @staticmethod
    def list_preview(obj):
        img_tag = '<img src="{}" width="75" height="75" style="margin:10px" />'
        preview = '<div>{images}</div>'
        images = ''.join(
            img_tag.format(image.image.url) for image in obj.images.all()
        )
        return mark_safe(preview.format(images=images))

    list_preview.short_description = 'List preview'
    list_preview.allow_tags = True


admin.site.register(Event, EventAdmin)
