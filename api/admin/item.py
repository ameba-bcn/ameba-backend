from django.forms.models import BaseInlineFormSet
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from django.contrib import admin

from api.models import (
    Discount, Item, ItemVariant, ItemAttribute, ItemAttributeType
)


class ItemVariantInline(admin.TabularInline):
    fields = ['attributes', 'stock', 'price']
    model = ItemVariant
    extra = 0
    verbose_name = 'Variant'
    verbose_name_plural = 'Variants'
    formset = BaseInlineFormSet


class DiscountChoiceInLine(admin.TabularInline):
    model = Discount.items.through
    extra = 0
    verbose_name = 'Discount'
    verbose_name_plural = 'Discounts'
    formset = BaseInlineFormSet
    fk_name = 'item'


class ImageChoiceInLine(admin.TabularInline):
    model = Item.images.through
    extra = 0
    verbose_name = 'Image'
    formset = BaseInlineFormSet
    fields = ('image', 'preview')
    readonly_fields = ('preview', )

    def preview(self, obj):
        img_tag = '<img src="{}" width="150" height="150" />'
        if obj.image:
            return mark_safe(img_tag.format(obj.image.url))

    preview.short_description = _('Preview')
    preview.allow_tags = True


class BaseItemAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'price', 'created', 'updated']
    inlines = [ItemVariantInline, ImageChoiceInLine, DiscountChoiceInLine]
    readonly_fields = ['created', 'updated', 'price']
    list_display = ['name', 'price', 'description', 'preview']

    def preview(self, obj):
        img_tag = '<img src="{}" width="75" height="75" style="margin:10px" />'
        preview = '<div>{images}</div>'
        images = ''.join(
            img_tag.format(image.image.url) for image in obj.images.all()
        )
        return mark_safe(preview.format(images=images))

    preview.short_description = _('Preview')
    preview.allow_tags = True


admin.site.register(Item, BaseItemAdmin)


class ItemAttributeAdmin(admin.ModelAdmin):
    fields = ('attribute', 'value')
    list_display = ('attribute', 'value')


admin.site.register(ItemAttribute, ItemAttributeAdmin)


class ItemAttributeTypeAdmin(admin.ModelAdmin):
    fields = ('name', )
    list_display = ('name', )


admin.site.register(ItemAttributeType, ItemAttributeTypeAdmin)
