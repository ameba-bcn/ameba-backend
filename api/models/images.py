from django.db import models
from django.utils.translation import ugettext_lazy as _


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
