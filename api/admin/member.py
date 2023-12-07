from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from api.models import Member, Membership, Subscription, MemberMediaUrl
from api.admin.image import get_image_preview

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
        return tuple(
            [(obj.name, obj.name) for obj in Subscription.objects.all()] +
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

class MemberProjectTagAdmin(TranslationAdmin):
    fields = ('name', )
    list_display = ('name', )


class MediaUrlsInLine(admin.StackedInline):
    model = MemberMediaUrl
    verbose_name = 'Member media url'
    verbose_name_plural = "Member media urls"
    fields = ('url', 'embedded', 'created')
    readonly_fields = ('created', )
    extra = 0



class MemberAdmin(admin.ModelAdmin):
    search_fields = ('number', 'user__email', 'first_name', 'last_name')
    list_display = (
        'number', 'user', 'first_name', 'last_name' , 'expires', 'status',
        'type', 'public', 'list_preview'
    )
    fields = (
        'number', 'user', 'first_name', 'last_name', 'project_name',
        'description', 'tags', 'genres', 'public', 'image', 'preview',
        'status', 'type', 'expires'
    )
    list_display_links = ('number', )
    readonly_fields = (
        'preview', 'list_preview', 'status', 'type', 'expires'
    )
    list_filter = (StatusFilter, TypeFilter)
    inlines = [MembershipInLine]

    def preview(self, obj):
        return get_image_preview(obj.image, 150)

    preview.short_description = 'Preview'
    preview.allow_tags = True

    def list_preview(self, obj):
        return get_image_preview(obj.image, 60)

    list_preview.short_description = 'Preview'
    list_preview.allow_tags = True


admin.site.register(Member, MemberAdmin)
