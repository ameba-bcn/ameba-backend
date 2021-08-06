from django.contrib import admin

from api.models import Member, Membership


class MembershipInLine(admin.TabularInline):
    model = Membership
    extra = 0
    verbose_name = 'Membership'
    fields = ('member', 'created', 'duration', 'starts', 'expires',
              'subscription', 'expires_soon', 'state', 'is_active',
              'is_expired')
    readonly_fields = (
        'created', 'duration', 'expires_soon', 'state', 'is_active',
        'is_expired'
    )


class MemberAdmin(admin.ModelAdmin):
    search_fields = ('number', 'user')
    list_display = (
        'number',
        'user',
        'address',
        'first_name',
        'last_name',
        'phone_number',
        'status',
        'type'
    )
    list_display_links = ('number', )
    inlines = [MembershipInLine]

    def group_display(self, obj):
        return ", ".join(group.name for group in obj.groups.all())


admin.site.register(Member, MemberAdmin)
