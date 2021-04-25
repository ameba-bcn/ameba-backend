from django.contrib import admin

from api.models import MailingList


class MailingListAdmin(admin.ModelAdmin):
    fields = ('address', 'count', 'is_test')
    list_display = ('address', 'count', 'is_test')
    readonly_fields = ('count', 'is_test')

    def count(self, obj):
        return obj.subscribers.count()


admin.site.register(MailingList, MailingListAdmin)
