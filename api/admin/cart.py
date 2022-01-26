from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

from api.models import Cart


class CartItemTabular(admin.TabularInline):
    model = Cart.item_variants.through
    extra = 0
    fields = ['item_variant', 'price', 'discount', 'subtotal', 'preview']
    readonly_fields = ['discount', 'preview', 'price', 'subtotal']

    def preview(self, obj):
        img_tag = '<img src="{}" width="75" height="75" />'
        if images  := obj.item_variant.images.all():
            return mark_safe(img_tag.format(images[0].url))

    preview.short_description = _('Preview')
    preview.allow_tags = True

    def price(self, obj):
        return f'{obj.item_variant.price}€'

    @staticmethod
    def subtotal(obj):
        price = float(obj.item_variant.price)
        fraction = 1. - float(obj.discount_value.value) / 100.
        return f'{price * fraction}€'

    price.short_description = _('Price')
    price.allow_tags = True


class CartAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'user__username')
    list_display_links = ('user',)
    list_display = ('user', 'id')
    fieldsets = [
        (None, {'fields': ['id', 'user', 'total', 'discount_code']})
    ]
    inlines = (CartItemTabular, )
    readonly_fields = ['id', 'total', 'computed_item_variants']


admin.site.register(Cart, CartAdmin)
