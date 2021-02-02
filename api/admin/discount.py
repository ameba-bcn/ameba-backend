from django.contrib import admin
from api.models import Discount, DiscountCode


class DiscountAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'value', 'items', 'groups',
                           'need_code', 'number_of_uses']})
    ]
    list_display = ['name', 'value', 'need_code', 'number_of_uses']


admin.site.register(Discount, DiscountAdmin)


class DiscountCodeAdmin(admin.ModelAdmin):
    fields = ['code', 'user', 'discount', 'days_period', 'is_expired']
    readonly_fields = ['is_expired']


admin.site.register(DiscountCode, DiscountCodeAdmin)
