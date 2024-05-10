from django.core.management.base import BaseCommand
import api.models as api_models
import logging

logger = logging.getLogger('regnerate_qrs')

class Command(BaseCommand):
    help = 'Resize and reformat all images in the media folder to fit ' \
           'maximum size and jpeg format.'

    def handle(self, *args, **options):
        for member in api_models.Member.objects.all():
            member.regenerate_qr()
            member.save()
            print(f'Processing {member.number}')
