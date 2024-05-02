from django.core.management.base import BaseCommand
import api.models as api_models


class Command(BaseCommand):
    help = 'Resize and reformat all images in the media folder to fit ' \
           'maximum size and jpeg format.'

    def handle(self, *args, **options):
        for image in api_models.Image.objects.all():
            image.save()
        for member_image in api_models.MemberProfileImage.objects.all():
            member_image.save()
        for collaborator in api_models.Collaborator.objects.all():
            collaborator.save()
        for interview in api_models.Interview.objects.all():
            interview.save()
