from django.db import models
from django.utils.translation import gettext_lazy as _
import api.images as img_utils


class Image(models.Model):
    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    image = models.ImageField(upload_to='images', verbose_name=_('image'))

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        return self.image.name

    def save(self, *args, **kwargs):
        if self.image:
            img_utils.replace_image_field(self.image)
        super().save(*args, **kwargs)
