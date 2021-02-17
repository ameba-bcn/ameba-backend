from django.contrib import admin

from api.admin.item import BaseItemAdmin
from api.models import Subscription


class SubscriptionAdmin(BaseItemAdmin):
    fieldsets = [
        (None, {'fields': ['id', 'name', 'description', 'benefits', 'price',
                           'stock', 'created', 'updated']})
    ]


admin.site.register(Subscription, SubscriptionAdmin)
