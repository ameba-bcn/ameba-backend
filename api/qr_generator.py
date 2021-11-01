import os
import urllib.parse

from django.conf import settings
import qrcode


def create_qr_code(url, qr_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    qr_path = os.path.join(settings.QR_TMP_DIR, f'{qr_id}.png')
    img.save(qr_path)
    return os.path.relpath(qr_path, settings.HTML_TMP_DIR)


def generate_member_card_qr(member, protocol, site_name):
    token = member.get_member_card_token()
    url_path = f'ameba-site/?token={token}'
    url = urllib.parse.urljoin(f'{protocol}://{site_name}', url_path)
    qr_code_path = create_qr_code(url, member.pk)
    return qr_code_path
