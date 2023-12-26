from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from api.models import MusicGenres


class MusicGenresAdmin(admin.ModelAdmin):
    fields = ('name', 'verbose', 'validated')
    readonly_fields = ('verbose', )
    list_display = ('name', 'verbose', 'validated')
    search_fields = ('name', )
    list_filter = ('validated', )

admin.site.register(MusicGenres, MusicGenresAdmin)
