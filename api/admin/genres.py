from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from api.models import MusicGenres


class MusicGenresAdmin(admin.ModelAdmin):
    fields = ('name', 'verbose')
    readonly_fields = ('verbose', )
    list_display = ('verbose', )


admin.site.register(MusicGenres, MusicGenresAdmin)
