from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        send_mail(
            'Email test',
            'Email enviado a jonrivala@gmail.com',
            'postmaster@email.ameba.jaguarintheloop.live',
            ['jonrivala@gmail.com'],
            fail_silently=False,
        )
