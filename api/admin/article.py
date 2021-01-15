from django.contrib import admin
from api.models import Item, ItemVariant, ItemImage, Discount
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
        (None, {'fields': ['name', 'description', 'price', 'stock',
                           'created', 'updated', 'event']})
    ]
    inlines = [ImageChoiceInLine, VariantChoiceInline, DiscountChoiceInLine]
    readonly_fields = ['created', 'updated', 'event']
    list_display = ['name', 'price', 'stock', 'description', 'preview']

    def preview(self, obj):
        img_tag = '<img src="{}" width="75" height="75" style="margin:10px" />'
        preview = '<div>{images}</div>'
        images = ''.join(
            img_tag.format(image.image.url) for image in obj.images.all()
        )
        return mark_safe(preview.format(images=images))

    def get_queryset(self, request):
        return Item.objects.filter(event=None)

    preview.short_description = _('Preview')
    preview.allow_tags = True


admin.site.register(Item, ItemAdmin)

