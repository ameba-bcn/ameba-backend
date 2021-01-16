from django.contrib import admin
from django.utils.html import mark_safe
from api.models import Image


def get_image_preview(image, size=150):
    return mark_safe(
        f'<img src="{image.url}" width="{size}" height="{size}" />'
    )


class ImageAdmin(admin.ModelAdmin):
    fields = ('image', 'preview')
    readonly_fields = ['preview', ]

    @staticmethod
    def preview(obj):
        return get_image_preview(obj.image)

    @staticmethod
    def list_preview(obj):
        return get_image_preview(obj.image, 75)


admin.site.register(Image, ImageAdmin)
