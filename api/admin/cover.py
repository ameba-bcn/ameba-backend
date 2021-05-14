from django.contrib import admin
from api.models import Cover


class CoverAdmin(admin.ModelAdmin):
    ordering = ('index', '-created')
    fields = ('file', 'is_active', 'index', 'created', 'extension')
    readonly_fields = ['created', 'extension']
    list_display = ('file', 'is_active', 'index', 'created', 'extension')
    search_fields = ('file', )


admin.site.register(Cover, CoverAdmin)
