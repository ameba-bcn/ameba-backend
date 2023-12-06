from django.contrib import admin
from django.utils.html import mark_safe
from modeltranslation.admin import TranslationAdmin

from api.models import MemberProject, MemberProjectMediaUrl, ArtistTag
from api.admin.image import get_image_preview


class MemberProjectTagAdmin(TranslationAdmin):
    fields = ('name', )
    list_display = ('name', )


class MediaUrlsInLine(admin.StackedInline):
    model = MemberProjectMediaUrl
    verbose_name = 'Member project media url'
    verbose_name_plural = "Member project media urls"
    fields = ('embedded', 'created')
    readonly_fields = ('created', )
    extra = 0


class MemberProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': [
                    'member', 'name', 'description', 'tags',
                    'public', 'image', 'preview', 'created'
                ]
            }
        )
    ]
    readonly_fields = ['preview']
    list_display = ['name', 'member', 'list_preview', 'public']
    inlines = (MediaUrlsInLine, )

    def preview(self, obj):
        preview = '<div>{images}</div>'
        images = get_image_preview(obj.image, 150)
        return mark_safe(preview.format(images=images))

    preview.short_description = 'Preview'
    preview.allow_tags = True

    def list_preview(self, obj):
        preview = '<div>{images}</div>'
        images = get_image_preview(obj.image, 75)
        return mark_safe(preview.format(images=images))

    list_preview.short_description = 'Preview'
    list_preview.allow_tags = True


admin.site.register(MemberProject, MemberProjectAdmin)
