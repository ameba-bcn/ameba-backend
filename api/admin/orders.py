from django.contrib import admin

from api.models import Order


class OrderAdmin(admin.ModelAdmin):
    fields = ['user', 'address', 'ready', 'delivered', 'created', 'updated']
    list_display = ['user', 'ready', 'delivered', 'updated', 'items']
    list_filter = ['user', 'delivered', 'ready']
    readonly_fields = ['items', 'created', 'updated']

    @staticmethod
    def items(obj):
        return len(obj.item_variants.all())


admin.site.register(Order, OrderAdmin)
