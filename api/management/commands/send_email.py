from django.core.management.base import BaseCommand
from api import email_factories
from api.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--template', dest='template')
        parser.add_argument('--mail_to', dest='mail_to',
                            default='jonrivala@gmail.com')

    def handle(self, *args, **options):
        template = options.get('template')

        if hasattr(email_factories, template):
            mail_to = options.get('mail_to')
            user = User.objects.get(email=mail_to)
            mail_template = getattr(email_factories, template)
            mail_template.send_to(
                mail_to=user.email,
                user=user
            )
