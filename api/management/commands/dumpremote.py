import os
import datetime
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_save, pre_save
import api.helpers.signaling as signaling


class Command(BaseCommand):
    help = 'Dump JSON data from the database'
    auth_file = 'api/fixtures/auth.json'
    data_file = 'api/fixtures/local.json'

    def handle(self, *args, **options):
        call_command(
            'dumpdata', 'auth.group', 'auth.permission', exclude=['background_task'], indent=2, natural_foreign=True,
            natural_primary=True, output=self.auth_file
        )
        call_command(
            'dumpdata', 'api', indent=2, natural_foreign=True, natural_primary=True,
            exclude=['background_task', 'auth.permission', 'contenttypes', 'auth.group', 'sessions'],
            output=self.data_file
        )
