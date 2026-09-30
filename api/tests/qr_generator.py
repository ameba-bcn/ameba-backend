import os

from PIL.Image import Image

from django.conf import settings

from api import qr_generator
from api import qr_factories
from api.models import Event
from api.tests.event import BaseEventTest
from api.tests.user import BaseUserTest


class TestGenerateEventTicketQr(BaseEventTest):
    def setUp(self):
        super().setUp()
        user_data = {
            'username': 'manolilto',
            'email': 'man@olito.com',
            'password': 'ameba12345'
        }
        self.user, _ = BaseUserTest._insert_user(user_data)
        self.event = Event.objects.all()[0]
        self.variant = self.event.variants.all()[0]
        self._generated_files = []

    def tearDown(self):
        super().tearDown()
        for file_path in self._generated_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_generate_event_ticket_qr_returns_path_to_existing_file(self):
        result = qr_generator.generate_event_ticket_qr(
            item_variant=self.variant,
            user=self.user,
            protocol='https',
            site_name='ameba.cat'
        )

        # Regression check: this used to return a raw PIL Image object
        # (which Django would render as its repr() string in the ticket
        # PDF template), instead of a path to a saved file on disk.
        self.assertIsInstance(result, str)
        self.assertNotIsInstance(result, Image)

        absolute_path = os.path.join(settings.HTML_TMP_DIR, result)
        self._generated_files.append(absolute_path)
        self.assertTrue(os.path.exists(absolute_path))

    def test_generate_event_ticket_qr_path_matches_expected_scheme(self):
        result = qr_generator.generate_event_ticket_qr(
            item_variant=self.variant,
            user=self.user,
            protocol='https',
            site_name='ameba.cat'
        )
        absolute_path = os.path.join(settings.HTML_TMP_DIR, result)
        self._generated_files.append(absolute_path)

        expected_name = f'e{self.variant.pk}u{self.user.pk}.png'
        self.assertTrue(result.endswith(expected_name))

    def test_event_ticket_pdf_does_not_contain_broken_qr_placeholder(self):
        qr_path = qr_generator.generate_event_ticket_qr(
            item_variant=self.variant,
            user=self.user,
            protocol='https',
            site_name='ameba.cat'
        )
        self._generated_files.append(os.path.join(settings.HTML_TMP_DIR, qr_path))

        pdf_card = qr_factories.EventTicketWithQr(
            identifier=f'{self.variant.pk}_{self.user.pk}',
            event=self.event,
            name='Manolilto',
            qr_path=qr_path
        )
        self._generated_files.append(pdf_card.attachment)

        self.assertTrue(os.path.exists(pdf_card.attachment))
        with open(pdf_card.attachment, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()

        self.assertGreater(len(pdf_bytes), 0)
        # A previous regression rendered the literal Python repr() of the
        # QR image object into the <img src="..."> attribute, which made
        # weasyprint fall back to alt="qr_code" text in the rendered PDF.
        self.assertNotIn(b'qr_code', pdf_bytes)
        self.assertNotIn(b'PIL.Image', pdf_bytes)
