import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import mark_safe
from modeltranslation.admin import TranslationAdmin

from api.admin.item import BaseItemAdmin
from api.models import Event, EventType



def export_participants_to_csv(modeladmin, request, queryset):
    """
    Exports selected events' participants to a CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ameba-event-list.csv"'

    writer = csv.writer(response)
    writer.writerow(['Email', 'Member Type', 'Status', 'Event', 'Date', 'Price'])

    for obj in queryset:
        for iv in obj.variants.all():
            for user in iv.acquired_by.all():
                member_type = user.member.type if hasattr(user, 'member') else 'not member'
                status = user.member.status if hasattr(user, 'member') else 'not member'
                writer.writerow([
                    user.email,
                    member_type,
                    status,
                    obj.name,
                    obj.datetime.isoformat(),
                    float(obj.price)
                ])

    return response

export_participants_to_csv.short_description = "Export participants to CSV"




class EventTypeAdmin(TranslationAdmin):
    fields = ('name', )
    list_display = ('name', )


class EventAdmin(BaseItemAdmin):
    fields = ['header'] + BaseItemAdmin.fields + ['datetime', 'address', 'maps_url', 'artists', 'type', 'participant_list', 'cancelled']
    readonly_fields = BaseItemAdmin.readonly_fields + ['participant_list']
    list_display = BaseItemAdmin.list_display[:3] + ['participants', 'cancelled'] + BaseItemAdmin.list_display[3:]
    actions = [export_participants_to_csv]

    @staticmethod
    def participants(obj):
        tot = 0
        for iv in obj.variants.all():
            tot += len(iv.acquired_by.all())
        return tot

    @staticmethod
    def participant_list(obj):
        row = """
            <tr>
                <td> {} </td>
                <td> {} </td>
                <td> {} </td>
            </tr>
        """
        rows = []
        for iv in obj.variants.all():
            for user in iv.acquired_by.all():
                rows.append(row.format(
                    user.email,
                    user.member.type if hasattr(user, 'member') else 'not member',
                    user.member.status if hasattr(user, 'member') else 'not member'
                ))

        return mark_safe(f"""
            <table>
                <tr>
                    <th>Email</th>
                    <th>Member type</th>
                    <th>Status</th>
                </tr>
                {''.join(rows)}
            </table>
        """)


admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
