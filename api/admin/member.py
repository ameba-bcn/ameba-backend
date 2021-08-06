from django.contrib import admin

from api.models import Member, Membership


class MembershipInLine(admin.TabularInline):
    model = Membership
    extra = 0
    verbose_name = 'Membership'


class MemberAdmin(admin.ModelAdmin):
    search_fields = ('number', 'user')
    list_display = (
        'number',
        'user',
        'address',
        'first_name',
        'last_name',
        'phone_number'
    )
    list_display_links = ('number', )
    inlines = [MembershipInLine]

    def group_display(self, obj):
        return ", ".join(group.name for group in obj.groups.all())


admin.site.register(Member, MemberAdmin)
