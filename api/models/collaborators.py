from django.db import models
from django.utils.translation import gettext_lazy as _


def get_default_order():
    return Collaborator.objects.count() + 1


class Collaborator(models.Model):
    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    image = models.ImageField(upload_to='images', verbose_name=_('image'))
    description = models.TextField(
        verbose_name=_('description'), blank=True, null=True
    )
    is_active = models.BooleanField(verbose_name=_('active'), default=True)
    order = models.IntegerField(
        verbose_name=_('order'),
        blank=True,
        default=get_default_order
    )

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        return self.image.name
