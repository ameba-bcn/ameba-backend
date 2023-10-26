from django.contrib import admin

from api.models import Member, Membership, Subscription


class StatusFilter(admin.SimpleListFilter):

    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'active'),
            ('expired', 'expired'),
            ('-', '-')
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        if value == '-':
            value = None

        id_list = [
            element.pk for element in queryset if element.status == value
        ]
        return queryset.filter(pk__in=id_list)


class TypeFilter(admin.SimpleListFilter):

    title = 'Type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return tuple([(obj.name, obj.name) for obj in Subscription.objects.all()] +
            [('-', '-')]
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        if value == '-':
            value = None

        id_list = [
            element.pk for element in queryset if element.type == value
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
    search_fields = ('number', 'user__email', 'first_name', 'last_name')
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
    list_filter = (StatusFilter, TypeFilter)
    inlines = [MembershipInLine]

    def group_display(self, obj):
        return ", ".join(group.name for group in obj.groups.all())


admin.site.register(Member, MemberAdmin)
