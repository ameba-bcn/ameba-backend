from django.contrib import admin

from api.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    fields = ['user', 'total', 'status', 'cart_record', 'details',
              'timestamp']
    readonly_fields = fields
    list_display = ['user', 'total', 'status', 'timestamp']
    list_filter = ['user']


admin.site.register(Payment, PaymentAdmin)
