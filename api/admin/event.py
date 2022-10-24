from django.contrib import admin
from django.utils.html import mark_safe
from modeltranslation.admin import TranslationAdmin

from api.admin.item import BaseItemAdmin
from api.models import Event, EventType


class EventTypeAdmin(TranslationAdmin):
    fields = ('name', )
    list_display = ('name', )


class EventAdmin(BaseItemAdmin):
    fields = ['header'] + BaseItemAdmin.fields + ['datetime', 'address', 'artists', 'type', 'participant_list']
    readonly_fields = BaseItemAdmin.readonly_fields + ['participants', 'participant_list']
    list_display = BaseItemAdmin.list_display[:3] + ['participants'] + BaseItemAdmin.list_display[3:]

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
                    user.member.type if hasattr(user, 'member') else '-',
                    user.member.status if hasattr(user, 'member') else '-'
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
