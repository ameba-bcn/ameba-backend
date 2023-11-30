from django.contrib import admin

from api.models import Payment


@admin.action(description="Close pending payments")
def close_payment(modeladmin, request, queryset):
    for payment in queryset:
        details = dict(invoice=dict(payment.invoice))
        details['invoice']['status'] = 'paid'
        details['payment_intent'] = 'payment_intent_id_12345'
        payment.details = details
        payment.save()
        payment.close()


class PaymentAdmin(admin.ModelAdmin):
    fields = ['user', 'total', 'status', 'cart_record', 'invoice',
              'timestamp']
    readonly_fields = fields
    list_display = ['user', 'total', 'status', 'timestamp']
    list_filter = ['user']
    actions = [close_payment]


admin.site.register(Payment, PaymentAdmin)
