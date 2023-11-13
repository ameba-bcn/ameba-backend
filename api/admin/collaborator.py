from django.contrib import admin
from api.models import Collaborator
from django.utils.html import mark_safe
from api.admin.image import get_image_preview


def preview_image_obj(obj):
    image = get_image_preview(obj, 150)
    return f'<div>{image}</div>'


def preview_video_obj(obj, ext):
    return f"""
    <div>
        <video height="150">
            <source src="{obj.url}#t=0.5" type="video/{ext}"/>
        </video>
    </div>
    """


def get_preview(obj):
    ext = obj.url.split('.')[-1].replace('/', '')
    if ext in ['mp4']:
        return preview_video_obj(obj, ext)
    elif ext in ['jpeg', 'gif', 'png', 'jpg']:
        return preview_image_obj(obj)


class CollaboratorAdmin(admin.ModelAdmin):
    ordering = ('order', )
    fields = ('name', 'image', 'is_active', 'order', 'preview')
    readonly_fields = ('preview', )
    list_display = ('name', 'image', 'is_active', 'order', 'preview')
    search_fields = ('name', )

    @staticmethod
    def preview(obj):
        return mark_safe(get_preview(obj))


admin.site.register(Collaborator, CollaboratorAdmin)
