from django.contrib import admin

from api.models import Artist


class ArtistAdmin(admin.ModelAdmin):
    search_fields = ('artistic_name', 'personal_name')
    list_display = (
        'artistic_name',
        'personal_name',
        'biography',
        'member',
        'updated',
        'created',
        'image'
    )
    list_display_links = ('artistic_name', 'personal_name')


admin.site.register(Artist, ArtistAdmin)
