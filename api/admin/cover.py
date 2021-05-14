from django.contrib import admin
from django.utils.html import mark_safe
from api.models import Cover


def get_image_preview(image, size=150):
    return mark_safe(
        f'<img src="{image.url}" width="{size}" height="{size}" />'
    )


class CoverAdmin(admin.ModelAdmin):
    ordering = ('index', '-created')
    fields = ('file', 'is_active', 'index', 'created', 'preview')
    readonly_fields = ['preview', 'created']
    list_display = ('file', 'is_active', 'index', 'created',
                    'list_preview')
    search_fields = ('file', )

    @staticmethod
    def preview(obj):
        return get_image_preview(obj.file)

    @staticmethod
    def list_preview(obj):
        return get_image_preview(obj.file, 75)


admin.site.register(Cover, CoverAdmin)
