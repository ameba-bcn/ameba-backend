import os

import qrcode


QR_DIR = "api/tmp/qr/"


def create_qr_code(url, qr_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    qr_path = os.path.join(QR_DIR, f'{qr_id}.png')
    img.save(qr_path)
    return qr_path
