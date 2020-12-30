from django.contrib import admin
from api.models import Item, ItemVariant, ItemImage
from django.forms.models import BaseInlineFormSet
from django.utils.html import mark_safe
from django.utils.translation import gettext as _


class VariantChoiceInline(admin.TabularInline):
    model = ItemVariant
    extra = 0
    verbose_name = 'Variant'
    formset = BaseInlineFormSet
    fields = ('name', 'stock', 'description', 'image', 'preview')
    readonly_fields = ('preview', )

    def preview(self, obj):
        img_tag = '<img src="{}" width="150" height="150" />'
        if obj.image:
            return mark_safe(img_tag.format(obj.image.url))

    preview.short_description = _('Preview')
    preview.allow_tags = True


class ImageChoiceInLine(admin.TabularInline):
    model = ItemImage
    extra = 0
    verbose_name = 'Image'
    formset = BaseInlineFormSet
    fields = ('image', 'active', 'preview')
    readonly_fields = ('preview', )

    def preview(self, obj):
        img_tag = '<img src="{}" width="150" height="150" />'
        if obj.image:
            return mark_safe(img_tag.format(obj.image.url))

    preview.short_description = _('Preview')
    preview.allow_tags = True


class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'description', 'price', 'stock']})
    ]
    inlines = [ImageChoiceInLine, VariantChoiceInline]
    list_display = ['name', 'price', 'stock', 'description', 'preview']

    def preview(self, obj):
        img_tag = '<img src="{}" width="75" height="75" style="margin:10px" />'
        preview = '<div>{images}</div>'
        images = ''.join(
            img_tag.format(image.image.url) for image in obj.images.all()
        )
        return mark_safe(preview.format(images=images))

    preview.short_description = _('Preview')
    preview.allow_tags = True


admin.site.register(Item, ItemAdmin)

