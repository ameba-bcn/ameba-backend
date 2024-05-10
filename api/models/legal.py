from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone

from api import cache_utils


class LegalDocument(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='legal/')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    position = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Legal Document')
        verbose_name_plural = _('Legal Documents')

    @property
    def size(self):
        return f'{self.file.size / 1024 / 1024:.2f} MB'

    @property
    def file_name(self):
        return self.file.name.split('/')[-1]

    def __str__(self):
        return self.title

    @cache_utils.invalidate_models_cache
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
