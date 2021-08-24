from django.contrib import admin
from django.utils.html import mark_safe
from modeltranslation.admin import TranslationAdmin

from api.models import Artist, ArtistMediaUrl, ArtistTag
from api.admin.image import get_image_preview


class ArtistTagAdmin(TranslationAdmin):
    fields = ('name', )
    list_display = ('name', )


class MediaUrlsInLine(admin.StackedInline):
    model = ArtistMediaUrl
    verbose_name = 'ArtistMediaUrl'
    verbose_name_plural = "ArtistMediaUrls"
    fields = ('url', 'created')
    readonly_fields = ('created', )
    extra = 0


class ArtistImages(admin.StackedInline):
    model = Artist.images.through
    verbose_name = 'ArtistImage'
    verbose_name_plural = 'ArtistImages'
    fields = ('image', )
    extra = 0


class ArtistAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['id', 'name', 'biography', 'tags']})
    ]
    readonly_fields = ['id', 'bio_preview']
    list_display = ['name', 'bio_preview', 'list_preview']
    inlines = (MediaUrlsInLine, ArtistImages)

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
admin.site.register(ArtistTag, ArtistTagAdmin)
