from django.db import models
from django.utils.translation import gettext_lazy as _
import api.images as img_utils


def get_default_order():
    return Collaborator.objects.count() + 1


class Collaborator(models.Model):
    class Meta:
        verbose_name = _('Collaborator')
        verbose_name_plural = _('Collaborators')

    name = models.CharField(max_length=50, verbose_name=_('name'))
    image = models.ImageField(upload_to='images', verbose_name=_('image'))
    description = models.TextField(
        verbose_name=_('description'), blank=True, null=True
    )
    is_active = models.BooleanField(verbose_name=_('active'), default=True)
    position = models.IntegerField(
        verbose_name=_('position'),
        blank=True,
        null=True,
        default=get_default_order
    )

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        return self.image.name

    def set_position(self, position):
        self.position = position
        self.save()

    def save(self, *args, **kwargs):
        if self.image:
            img_utils.replace_image_field(self.image)
        super().save(*args, **kwargs)
