from django.forms.models import BaseInlineFormSet
from django.contrib import admin

from api.admin.item import (
    BaseItemAdmin, ImageChoiceInLine, DiscountChoiceInLine, ItemVariantInline
)
from api.models import Subscription, ItemVariant


class EventVariantInline(admin.TabularInline):
    fields = ['id', 'attributes', 'stock', 'price', 'recurrence',
              'acquired_by']
    readonly_fields = ('id', )
    model = ItemVariant
    extra = 0
    verbose_name = 'Variant'
    verbose_name_plural = 'Variants'
    formset = BaseInlineFormSet


class SubscriptionAdmin(BaseItemAdmin):
    fields = BaseItemAdmin.fields + ['benefits', 'group']
    inlines = [ImageChoiceInLine, EventVariantInline, DiscountChoiceInLine]


admin.site.register(Subscription, SubscriptionAdmin)
