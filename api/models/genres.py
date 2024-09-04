from django.utils.translation import gettext_lazy as _
from django.db import models
import api.cache_utils as cache_utils


class MusicGenresManager(models.Manager):
    def create(self, *args, **kwargs):
        name = MusicGenres.normalize_name(kwargs['name'])
        if MusicGenres.objects.filter(name=name).exists():
            return MusicGenres.objects.get(name=name)
        return super().create(*args, **kwargs)

    def get_or_create(self, *args, **kwargs):
        kwargs['name'] = MusicGenres.normalize_name(kwargs['name'])
        return super().get_or_create(*args, **kwargs)


class MusicGenres(models.Model):
    class Meta:
        verbose_name = _('Music genre')
        verbose_name_plural = _('Music genres')

    name = models.CharField(
        max_length=20, unique=True, verbose_name=_('name'), primary_key=True
    )
    validated = models.BooleanField(default=False, verbose_name=_('validated'))
    objects = MusicGenresManager()

    def __str__(self):
        return self.verbose

    @staticmethod
    def normalize_name(name):
        return name.replace('.', '').replace('-', ' ').replace(' ', '_').upper()

    @property
    def verbose(self):
        return self.name.replace('_', ' ').capitalize()

    @cache_utils.invalidate_models_cache
    def save(self, *args, **kwargs):
        self.name = self.normalize_name(self.name)
        super().save(*args, **kwargs)
