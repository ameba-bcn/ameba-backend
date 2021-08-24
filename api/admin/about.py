from django.contrib import admin
from api.models import About
from modeltranslation.admin import TranslationAdmin


class AboutAdmin(TranslationAdmin):
    ordering = ('-created', '-updated')
    fields = ('text', 'is_active', 'created', 'updated')
    readonly_fields = ['preview', 'created', 'updated']
    list_display = ('preview', 'is_active', 'created', 'updated')


admin.site.register(About, AboutAdmin)
