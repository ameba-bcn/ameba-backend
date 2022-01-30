from django.contrib import admin
from django.utils.html import mark_safe

import api.models as api_models
from api.admin.image import get_image_preview


class OrderToItemVariantInLine(admin.TabularInline):
    model = api_models.Order.item_variants.through
    verbose_name = 'ItemVariant'
    verbose_name_plural = "ItemVariants"
    fields = ('itemvariant', 'name', 'stock', 'preview', )
    readonly_fields = ('name', 'stock', 'preview', )
    extra = 0

    @staticmethod
    def name(obj):
        return obj.itemvariant.name

    @staticmethod
    def stock(obj):
        return obj.itemvariant.stock

    @staticmethod
    def preview(obj):
        preview = '<div>{images}</div>'
        images = ''.join(get_image_preview(image, 75) for image in
                        obj.itemvariant.item.images.all())
        return mark_safe(preview.format(images=images))


class OrderAdmin(admin.ModelAdmin):
    fields = ['user', 'address', 'ready', 'delivered', 'created', 'updated']
    list_display = ['user', 'ready', 'delivered', 'updated', 'items']
    list_filter = ['user', 'delivered', 'ready']
    readonly_fields = ['items', 'created', 'updated']
    inlines = [OrderToItemVariantInLine]

    @staticmethod
    def items(obj):
        return len(obj.item_variants.all())


admin.site.register(api_models.Order, OrderAdmin)
