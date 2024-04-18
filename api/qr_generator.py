import os
import urllib.parse

from django.conf import settings
import qrcode


def create_qr_code(url, qr_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill=(29, 29, 28), back_color=(249, 229, 197))
    qr_path = os.path.join(settings.QR_TMP_DIR, f'{qr_id}.png')
    img.save(qr_path)
    return os.path.relpath(qr_path, settings.HTML_TMP_DIR)


def update_member_qr_image(member, tmp_qr_path):
    # Open temporary qr path image and save into member qr image field
    with open(tmp_qr_path, 'rb') as qr_file:
        member.qr.save(f'qr-member-{member.pk}.png', qr_file)


def generate_member_card_qr(member, protocol, site_name):
    token = member.get_member_card_token()
    url_path = settings.FE_MEMBERSHIP_CARD_PATH.format(token=token)
    url = urllib.parse.urljoin(f'{protocol}://{site_name}', url_path)
    qr_code_path = create_qr_code(url, member.pk)
    update_member_qr_image(member, qr_code_path)
    return qr_code_path


def generate_event_ticket_qr(item_variant, user, protocol, site_name):
    token = user.get_event_token(item_variant_id=item_variant.pk)
    url_path = settings.FE_EVENT_TICKET_PATH.format(token=token)
    url = urllib.parse.urljoin(f'{protocol}://{site_name}', url_path)
    qr_code_path = create_qr_code(url, f'e{item_variant.id}u{user.id}')
    return qr_code_path
