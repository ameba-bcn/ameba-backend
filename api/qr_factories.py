import os

import django.utils.encoding as encoding
from django.conf import settings
import django.utils.http as http
import django.template.loader as loader
from rest_framework_simplejwt.tokens import RefreshToken
import weasyprint


site_name = getattr(settings, 'HOST_NAME', '')


def user_token_generator(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


def encode_uid(pk):
    return http.urlsafe_base64_encode(encoding.force_bytes(pk))


class BaseQrFactory:
    html_body_template = None
    file_name_template = 'ameba_soci_{identifier}.pdf'

    def __init__(self, identifier, **context):
        self.attachment = self.create(
            self.file_name_template.format(identifier=identifier),
            self.html_body_template,
            context
        )

    @staticmethod
    def create(file_name, html_body, context):
        assert html_body
        html_body = loader.render_to_string(html_body, context)
        pdf_file_path = os.path.join(settings.PDF_TMP_DIR, file_name)
        html_doc = weasyprint.HTML(string=html_body, base_url=settings.HTML_TMP_DIR)
        pdf = html_doc.write_pdf()
        with open(pdf_file_path,  'wb') as pdf_file:
            pdf_file.write(pdf)
        return pdf_file_path


class MemberCardWithQr(BaseQrFactory):
    html_body_template = 'html_qr_documents/member_card_with_qr.html'


class EventTicketWithQr(BaseQrFactory):
    html_body_template = 'html_qr_documents/event_ticket_with_qr.html'
