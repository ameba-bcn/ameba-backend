from django.utils.translation import gettext_lazy as _
from django.db import models


class MusicGenres(models.Model):
    class Meta:
        verbose_name = _('Music genre')
        verbose_name_plural = _('Music genres')

    name = models.CharField(
        max_length=20, unique=True, verbose_name=_('name'), primary_key=True
    )

    def __str__(self):
        return self.verbose

    def verbose_name(self):
        return self._meta.verbose_name

    @staticmethod
    def normalize_name(name):
        return name.replace(' ', '_').lower()

    @property
    def verbose(self):
        return self.name.replace('_', ' ').capitalize()

    def save(self, *args, **kwargs):
        self.name = self.normalize_name(self.name)
        super().save(*args, **kwargs)
