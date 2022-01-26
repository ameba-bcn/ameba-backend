from django.contrib import admin
from api.models import Cover
from django.utils.html import mark_safe


def preview_image_obj(obj):
    return f'<div>get_image_preview({obj}, 150)</div>'


def preview_video_obj(obj, ext):
    return f"""
    <div>
        <video height = "100">
            <source src="{obj.url}#t=0.5" type="video/{ext}"/>
        </video>
    </div>
    """


def get_preview(obj):
    ext = obj.url.split('.')[-1].replace('/', '')
    if ext in ['mp4']:
        return preview_video_obj(obj, ext)
    elif ext in ['jpeg', 'gif', 'png']:
        return preview_image_obj(obj)


class CoverAdmin(admin.ModelAdmin):
    ordering = ('index', '-created')
    fields = ('file', 'is_active', 'index', 'created', 'extension')
    readonly_fields = ['created', 'preview', 'extension']
    list_display = ('file', 'is_active', 'index', 'created', 'extension',
                    'preview')
    search_fields = ('file', )

    @staticmethod
    def preview(obj):
        return mark_safe(get_preview(obj))


admin.site.register(Cover, CoverAdmin)
