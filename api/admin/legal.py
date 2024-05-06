from django.contrib import admin
from api.models import LegalDocument


class LegalAdmin(admin.ModelAdmin):
    ordering = ('index', '-created')
    fields = ('title', 'description', 'file_name', 'file', 'created', 'updated', 'is_active', 'order')
    readonly_fields = ['file_name', 'size', 'created', 'updated']
    list_display = ('title', 'file_name', 'size', 'created', 'updated', 'is_active')
    search_fields = ('title', 'description')


admin.site.register(LegalDocument, LegalAdmin)
