from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
import api.cache_utils as cache_utils

BIO_PREVIEW = 160


class ArtistTag(models.Model):
    class Meta:
        verbose_name = _('Artist tag')
        verbose_name_plural = _('Artist tags')

    name = models.CharField(max_length=20, unique=True, verbose_name=_('name'))

    def __str__(self):
        return f"{self.name}"


class ArtistMediaUrl(models.Model):
    class Meta:
        verbose_name = _('Artist media url')
        verbose_name_plural = _('Artist media urls')

    url = models.URLField(verbose_name=_('url'))
    embedded = models.TextField(max_length=2000, blank=True)
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )
    artist = models.ForeignKey(
        to='Artist', on_delete=models.CASCADE, related_name='media_urls',
        verbose_name=_('artist')
    )

    def __str__(self):
        return self.url


class Artist(models.Model):
    class Meta:
        verbose_name = _('Artist')
        verbose_name_plural = _('Artists')

    name = models.CharField(max_length=50, verbose_name=_('name'))
    biography = models.TextField(max_length=2500, verbose_name=_('biography'))
    images = models.ManyToManyField(
        to='Image', blank=True, verbose_name=_('images')
    )
    tags = models.ManyToManyField(
        to='ArtistTag', blank=True, verbose_name=_('tags')
    )
    is_ameba_dj = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def bio_preview(self):
        return self.biography[:BIO_PREVIEW]

    @property
    def has_interview(self):
        return bool(self.interview_set.filter(is_active=True))

    @property
    def interview(self):
        if self.has_interview:
            return self.interview_set.filter(
                is_active=True).order_by('-created').first()
        return None

    @cache_utils.invalidate_models_cache
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)