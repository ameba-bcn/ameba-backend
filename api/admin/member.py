from django.contrib import admin

from api.models import Member, Membership


class StatusFilter(admin.SimpleListFilter):

    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Status'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'active'),
            ('expired', 'expired'),
            ('-', '-')
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == '-':
            value = None

        id_list = [
            element.pk for element in queryset if element.status == value
        ]
        return queryset.filter(pk__in=id_list)


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
        'first_name',
        'last_name',
        'phone_number',
        'status',
        'type'
    )
    list_display_links = ('number', )
    list_filter = (StatusFilter, )
    inlines = [MembershipInLine]

    def group_display(self, obj):
        return ", ".join(group.name for group in obj.groups.all())


admin.site.register(Member, MemberAdmin)
