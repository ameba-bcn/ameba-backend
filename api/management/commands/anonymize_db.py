from django.utils.timezone import now
from django.core.management.base import BaseCommand
from api import email_factories
from api.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--confirmation', dest='confirmation')
        parser.add_argument('--mails', dest='mail_to', default='dev@ameba.cat')

    def handle(self, *args, **options):
        if now().strftime('%Y%m%d%H%M') != options.get('confirmation'):
            return "Confirmation code is not valid (date)"

        for user in User.objects.all():
            if user.email in options.get('mail_to').split(','):
                mail_template = getattr(email_factories, 'RenewalConfirmation')
                mail_template.send_to(
                    mail_to=user.email,
                    user=user
                )