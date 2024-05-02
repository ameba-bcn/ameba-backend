from django.core.management.base import BaseCommand
import api.models as api_models
import logging

logger = logging.getLogger('resize_images')

class Command(BaseCommand):
    help = 'Resize and reformat all images in the media folder to fit ' \
           'maximum size and jpeg format.'

    @staticmethod
    def process_images(model, field):
        for obj in model.objects.all():
            old_image_field = getattr(obj, field)
            obj.save()
            new_image_field = getattr(obj, field)
            print(
                f'Processing {old_image_field.name} --> {new_image_field.name}'
            )

    def handle(self, *args, **options):
        self.process_images(api_models.Image, 'image')
        self.process_images(api_models.MemberProfileImage, 'image')
        self.process_images(api_models.Collaborator, 'image')
        self.process_images(api_models.Interview, 'image')