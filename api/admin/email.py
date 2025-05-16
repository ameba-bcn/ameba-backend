from django.utils.safestring import mark_safe
from django.contrib import admin, messages
from modeltranslation.admin import TranslationAdmin
from api.email_factories import UserEmailFactoryBase
from api.models import Email
import json

class EmailAdmin(TranslationAdmin):
    fields = ('name', 'subject', 'content', 'base_template', 'example_context', 'preview')
    list_display = ('name', 'subject')
    search_fields = ('name', 'subject')
    actions = ['send_test_email']
    readonly_fields = ('preview',)

    @admin.display(description="Vista previa del email (HTML generado)")
    def preview(self, obj):
        if not obj:
            return ""

        # Obtener contexto
        try:
            context = obj.example_context
            if isinstance(context, str):
                context = json.loads(context)
        except Exception as e:
            return mark_safe(f"<p style='color: red;'>Error cargando contexto: {e}</p>")

        # Construir email usando EmailFactory
        try:
            context['protocol'] = 'http'
            context['site_name'] = 'localhost:8000'
            context['domain'] = 'localhost:8000'
            email_obj = UserEmailFactoryBase(mail_to='someone@example.com', db_email_name=obj.name, **context)
            html_content = email_obj.get_html_message()
            return mark_safe(html_content)
        except Exception as e:
            return mark_safe(f"<p style='color: red;'>Error generando el email: {e}</p>")


    @admin.action(description="Generar email de prueba")
    def send_test_email(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Por favor selecciona un email para hacer la prueba.", level=messages.WARNING)
            return

        email_obj = queryset.first()

        # Obtener el contexto desde example_context
        # try:
        context = email_obj.example_context
        if isinstance(context, str):
            context = json.loads(context)  # Por si example_context es texto en la DB
        # except Exception as e:
        #     self.message_user(request, f"Error procesando el contexto: {e}", level=messages.ERROR)
        #     return

        # Email de prueba (puedes cambiar esto o pedirlo dinámico)
        test_email = request.user.email or "test@example.com"

        # Enviar usando EmailFactory
        # try:
        context['protocol'] = 'http'
        context['site_name'] = 'localhost:8000'
        context['domain'] = 'localhost:8000'

        UserEmailFactoryBase.send_to(
            mail_to=test_email,
            db_email_name=email_obj.name,
            **context
        )
        self.message_user(request, f"Email de prueba enviado a {test_email}", level=messages.SUCCESS)
        # except Exception as e:
        #     self.message_user(request, f"Error enviando el email de prueba: {e}", level=messages.ERROR)



admin.site.register(Email, EmailAdmin)
