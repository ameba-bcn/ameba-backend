from django.db import models
from django.utils.translation import gettext_lazy as _


class Collaborator(models.Model):
    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    image = models.ImageField(upload_to='images', verbose_name=_('image'))
    description = models.TextField(
        verbose_name=_('description'), blank=True, null=True
    )
    active = models.BooleanField(verbose_name=_('active'), default=True)

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        return self.image.name
