import os
import datetime
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from api.helpers import anonymization


class Command(BaseCommand):
    help = 'Load JSON data into the database'
    fixtures_file = 'api/fixtures/local.json'
    media_file = 'api/fixtures/media.tgz'

    def handle(self, *args, **options):
        if settings.DEBUG is False or os.getenv('HOST_NAME') != 'localhost':
            raise Exception(
                'This command can only be run in debug mode and '
                'localhost environment.'
            )
        call_command('loaddata', self.fixtures_file)
        media_path = os.path.join(settings.MEDIA_ROOT, os.path.pardir)
        self.decompress_tar_file(self.media_file, media_path)

    @staticmethod
    def decompress_tar_file(file_path, target_path):
        import tarfile
        with tarfile.open(file_path, 'r') as tar:
            tar.extractall(target_path)
        return target_path
