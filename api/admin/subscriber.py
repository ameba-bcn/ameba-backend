from django.contrib import admin

from api.models import Subscriber


class SubscriberAdmin(admin.ModelAdmin):
    fields = ('email', 'mailing_lists')
    list_display = ('email', 'mailing_list_count')
    readonly_fields = ('mailing_list_count', )

    def mailing_list_count(self, obj):
        return obj.mailing_lists.count()


admin.site.register(Subscriber, SubscriberAdmin)
