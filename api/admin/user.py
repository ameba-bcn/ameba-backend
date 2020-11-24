from django.contrib import admin

from api.models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username')
    list_display = (
        'email',
        'username',
        'password',
        'is_active',
        'is_staff',
        'date_joined',
        'member'
    )
    list_display_links = ('email', 'username')

    def group_display(self, obj):
        return ", ".join(group.name for group in obj.groups.all())


admin.site.register(User, UserAdmin)

