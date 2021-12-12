from django.utils.translation import gettext_lazy as _
from django.db import models


class Cover(models.Model):
    class Meta:
        verbose_name = _('Cover')
        verbose_name_plural = _('Covers')

    file = models.FileField(upload_to='covers', verbose_name=_('file'))
    is_active = models.BooleanField(verbose_name=_('is active'))
    index = models.IntegerField(verbose_name=_('index'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )

    @property
    def url(self):
        return self.file.url

    def __str__(self):
        return self.file.name

    @property
    def extension(self):
        return self.file.name.split('.')[-1]
