from django.contrib import admin
from api.models import Discount


class DiscountAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'value', 'items', 'groups',
                           'need_code', 'number_of_uses']})
    ]
    list_display = ['name', 'value', 'need_code', 'number_of_uses']


admin.site.register(Discount, DiscountAdmin)
