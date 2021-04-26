from django.contrib import admin
from api.models import (
    Article, ArticleAttribute, Discount, ArticleFamily, ArticleAttributeType
)
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


class AttributesInLine(admin.TabularInline):
    model = Article.attributes.through
    extra = 0
    verbose_name = 'Attribute'
    formset = BaseInlineFormSet
    # fields = ('attribute', 'value')


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
        (None, {'fields': ['article_name', 'family', 'description', 'price', 'stock',
                           'created', 'updated']})
    ]
    inlines = [ImageChoiceInLine, AttributesInLine, DiscountChoiceInLine]
    readonly_fields = ['article_name', 'created', 'updated']
    list_display = ['article_name', 'price', 'stock', 'description', 'preview']

    @staticmethod
    def article_name(obj):
        return obj.__str__()

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


class ArticleFamilyAdmin(admin.ModelAdmin):
    fields = ('name', 'images', 'description')
    list_display = ['name']


admin.site.register(ArticleFamily, ArticleFamilyAdmin)


class ArticleAttributesAdmin(admin.ModelAdmin):
    fields = ('attribute', 'value')
    list_display = ('attribute', 'value')


admin.site.register(ArticleAttribute, ArticleAttributesAdmin)


class ArticleAttributeTypeAdmin(admin.ModelAdmin):
    fields = ('name', )
    list_display = ('name', )


admin.site.register(ArticleAttributeType, ArticleAttributeTypeAdmin)
