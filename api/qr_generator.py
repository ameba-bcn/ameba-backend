import os
import io
import urllib.parse

from django.conf import settings
from django.core.files.base import ContentFile
import qrcode


def create_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill=(29, 29, 28), back_color=(249, 229, 197))
    return img


def update_member_qr_image(member, tmp_qr_path):
    # Open temporary qr path image and save into member qr image field
    with open(tmp_qr_path, 'rb') as qr_file:
        image_name = f'{member.qr_hash}.png'
        member.qr.save(image_name, qr_file)


def generate_member_card_qr(token, site_name):
    url_path = settings.FE_MEMBERSHIP_CARD_PATH.format(token=token)
    protocol = settings.DEBUG and 'http' or 'https',
    url = urllib.parse.urljoin(f'{protocol}://{site_name}/', url_path)
    qr_img = create_qr_code(url)
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    image_file = ContentFile(buffer.getvalue())
    return image_file


def generate_event_ticket_qr(item_variant, user, protocol, site_name):
    token = user.get_event_token(item_variant_id=item_variant.pk)
    url_path = settings.FE_EVENT_TICKET_PATH.format(token=token)
    url = urllib.parse.urljoin(f'{protocol}://{site_name}', url_path)
    qr_code_path = create_qr_code(url, f'e{item_variant.id}u{user.id}')
    return qr_code_path
