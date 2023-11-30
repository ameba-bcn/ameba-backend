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


class MemberProjectImages(admin.StackedInline):
    model = MemberProject.images.through
    verbose_name = 'Member project image'
    verbose_name_plural = 'Member project images'
    fields = ('image', )
    extra = 0


class MemberProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': [
                    'id', 'member', 'name', 'description', 'tags', 'public', 'created'
                ]
            }
        )
    ]
    readonly_fields = ['id']
    list_display = ['name', 'member', 'list_preview', 'public']
    inlines = (MediaUrlsInLine, MemberProjectImages)

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


admin.site.register(MemberProject, MemberProjectAdmin)
