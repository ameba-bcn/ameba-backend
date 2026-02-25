import os
import datetime
from django.core.management.base import BaseCommand

import api.helpers.anonymization as anonymization


class Command(BaseCommand):
    help = """Anonymize the database. To use this command, set the environment variable ANONYMIZATION_DATE 
    to the current date and time in the format YYYYMMDDHHMM, and run the command on the server. This is a 
    safety measure to prevent accidental anonymization of the database."""

    def handle(self, *args, **options):
        anonymization.anonymize_database()
