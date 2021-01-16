from django.contrib import admin
from django.utils.html import mark_safe

from api.models import Artist
from api.admin.image import get_image_preview


class ArtistAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'biography']})
    ]
    readonly_fields = ['bio_preview']
    list_display = ['name', 'bio_preview', 'list_preview']

    def preview(self, obj):
        preview = '<div>{images}</div>'
        images = ''.join(
            get_image_preview(image, 150) for image in obj.images.all()
        )
        return mark_safe(preview.format(images=images))

    preview.short_description = 'Preview'
    preview.allow_tags = True

    def list_preview(self, obj):
        preview = '<div>{images}</div>'
        images = ''.join(
            get_image_preview(image, 75) for image in obj.images.all()
        )
        return mark_safe(preview.format(images=images))

    list_preview.short_description = 'Preview'
    list_preview.allow_tags = True


admin.site.register(Artist, ArtistAdmin)
