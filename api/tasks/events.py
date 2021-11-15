from background_task import background
from django.conf import settings

from api import qr_generator
from api import qr_factories
from api import email_factories
from api import models as api_models


#@background(schedule=0)
def generate_event_ticket_and_send_confirmation_email(item_variant_id,
                                                      user_id):
    user = api_models.User.objects.get(pk=user_id)
    item_variant = api_models.ItemVariant.objects.get(pk=item_variant_id)

    # Generate pdf with qr here
    qr_path = qr_generator.generate_event_ticket_qr(
        user=user,
        item_variant=item_variant,
        protocol=settings.DEBUG and 'http' or 'https',
        site_name=settings.HOST_NAME
    )
    pdf_card = qr_factories.EventTicketWithQr(
        identifier=f'{item_variant.pk}_{user.pk}',
        event=item_variant.item.event,
        useR=user,
        qr_path=qr_path
    )
    email_factories.EventConfirmationEmail.send_to(
        attachment=pdf_card.attachment,
        mail_to=user.email,
        user=user,
        event=item_variant.item.event,
        site_name=settings.HOST_NAME,
        protocol=settings.DEBUG and 'http' or 'https'
    )
