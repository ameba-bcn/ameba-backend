from django.db import models
from django.utils.translation import gettext_lazy as _


class Manifest(models.Model):

    class Meta:
        verbose_name = _('Manifest')
        verbose_name_plural = _('Manifests')

    text = models.TextField(verbose_name=_('text'))
    is_active = models.BooleanField(verbose_name=_('is_active'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

    @property
    def preview(self):
        return self.text[:15]
