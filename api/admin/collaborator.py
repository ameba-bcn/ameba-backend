from django.contrib import admin
from api.models import Collaborator
from django.utils.html import mark_safe
from api.admin.image import get_image_preview
from django.contrib import messages


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


def set_position(request, queryset, position):
    if len(queryset) != 1:
        messages.add_message(
            request, messages.WARNING, 'Only one collaborator change at a time'
        )
        return
    queryset.first().set_position(position)

@admin.action(description="Set order to 1")
def set_first(modeladmin, request, queryset):
    set_position(request, queryset, 1)

@admin.action(description="Set order to 2")
def set_second(modeladmin, request, queryset):
    set_position(request, queryset, 2)


@admin.action(description="Set order to 3")
def set_third(modeladmin, request, queryset):
    set_position(request, queryset, 3)


@admin.action(description="Set order to 4")
def set_fourth(modeladmin, request, queryset):
    set_position(request, queryset, 4)


@admin.action(description="Set order to 5")
def set_fifth(modeladmin, request, queryset):
    set_position(request, queryset, 5)


@admin.action(description="Set order to 6")
def set_sixth(modeladmin, request, queryset):
    set_position(request, queryset, 6)


@admin.action(description="Set order to 7")
def set_seventh(modeladmin, request, queryset):
    set_position(request, queryset, 7)


@admin.action(description="Set order to 8")
def set_eighth(modeladmin, request, queryset):
    set_position(request, queryset, 8)


@admin.action(description="Set order to 9")
def set_ninth(modeladmin, request, queryset):
    set_position(request, queryset, 9)


@admin.action(description="Set order to 10")
def set_tenth(modeladmin, request, queryset):
    set_position(request, queryset, 10)


class CollaboratorAdmin(admin.ModelAdmin):
    ordering = ('position', )
    fields = ('name', 'image', 'is_active', 'position', 'preview')
    readonly_fields = ('preview', )
    list_display = ('name', 'image', 'is_active', 'position', 'preview')
    search_fields = ('name', )
    actions = [set_first, set_second, set_third, set_fourth, set_fifth,
               set_sixth, set_seventh, set_eighth, set_ninth, set_tenth]

    @staticmethod
    def preview(obj):
        return mark_safe(get_preview(obj))


admin.site.register(Collaborator, CollaboratorAdmin)
