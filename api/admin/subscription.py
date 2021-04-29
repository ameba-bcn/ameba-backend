from django.contrib import admin

from api.admin.item import (
    BaseItemAdmin, ImageChoiceInLine, DiscountChoiceInLine, ItemVariantInline
)
from api.models import Subscription


class SubscriptionVariantInline(ItemVariantInline):
    fields = ItemVariantInline.fields + ['benefits']


class SubscriptionAdmin(BaseItemAdmin):
    inlines = [SubscriptionVariantInline, ImageChoiceInLine,
               DiscountChoiceInLine]


admin.site.register(Subscription, SubscriptionAdmin)
