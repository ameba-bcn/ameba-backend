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
    writer.writerow([
        'Número', 'Email', 'Nombre', 'Appellidos', 'Caducidad', 'Estado',
        'Member Type', 'Event', 'Date'
    ])

    for obj in queryset:
        for iv in obj.variants.all():
            for user in iv.acquired_by.all():
                number = user.member.number if hasattr(user, 'member') else '-'
                name = user.member.first_name if hasattr(user, 'member') else '-'
                last_name = user.member.last_name if hasattr(user, 'member') else '-'
                expires = user.member.expires if hasattr(user, 'member') else '-'
                status = user.member.status if hasattr(user, 'member') else '-'
                member_type = user.member.type if hasattr(user, 'member') else 'not member'
                writer.writerow([number, user.email, name, last_name, expires,
                    status, member_type, obj.name, obj.datetime.isoformat()
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
                <td> {} </td>
                <td> {} </td>
                <td> {} </td>
                <td> {} </td>
            </tr>
        """
        rows = []
        for iv in obj.variants.all():
            for user in iv.acquired_by.all():
                rows.append(row.format(
                    user.member.number if hasattr(user, 'member') else '-',
                    user.email,
                    user.member.first_name if hasattr(user, 'member') else '-',
                    user.member.last_name if hasattr(user, 'member') else '-',
                    user.member.expires if hasattr(user, 'member') else '-',
                    user.member.status if hasattr(user, 'member') else '-',
                    user.member.type if hasattr(user, 'member') else 'not member'
                ))

        return mark_safe(f"""
            <table>
                <tr>
                    <th>Número</th>
                    <th>Email</th>
                    <th>Nombre</th>
                    <th>Apellidos</th>
                    <th>Caducidad</th>
                    <th>Estado</th>
                    <th>Tipo</th>
                </tr>
                {''.join(rows)}
            </table>
        """)


admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
