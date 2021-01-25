from django.contrib import admin
from api.models import Discount, Item
from django.forms.models import BaseInlineFormSet
from django.utils.html import mark_safe
from django.utils.translation import gettext as _


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
    fieldsets = [
        (None, {'fields': ['name', 'description', 'price', 'stock',
                           'created', 'updated']})
    ]
    inlines = [ImageChoiceInLine, DiscountChoiceInLine]
    readonly_fields = ['created', 'updated']
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


# admin.site.register(Item, BaseItemAdmin)
