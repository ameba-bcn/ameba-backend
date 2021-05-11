from django.contrib import admin

from api.admin.item import (
    BaseItemAdmin, ImageChoiceInLine, DiscountChoiceInLine, ItemVariantInline
)
from api.models import Subscription


class SubscriptionAdmin(BaseItemAdmin):
    fields = BaseItemAdmin.fields + ['benefits', 'group']


admin.site.register(Subscription, SubscriptionAdmin)
