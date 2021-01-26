from django.contrib import admin
from api.models import Article, ArticleSize, Image, Discount
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


class SizeChoiceInline(admin.TabularInline):
    model = ArticleSize
    extra = 0
    verbose_name = 'Size'
    formset = BaseInlineFormSet
    fields = ('size', 'genre', 'stock')


class ImageChoiceInLine(admin.TabularInline):
    model = Article.images.through
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


class ArticleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'description', 'price', 'stock',
                           'created', 'updated']})
    ]
    inlines = [ImageChoiceInLine, SizeChoiceInline, DiscountChoiceInLine]
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


admin.site.register(Article, ArticleAdmin)

