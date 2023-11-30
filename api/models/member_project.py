from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models

from api.models import ArtistMediaUrl


DESCRIPTION_PREVIEW = 160


class MemberProjectMediaUrl(ArtistMediaUrl):
    artist = None
    member = models.ForeignKey(
        to='MemberProject', on_delete=models.CASCADE, related_name='media_urls',
        verbose_name=_('artist')
    )

    class Meta:
        verbose_name = _('Project media url')
        verbose_name_plural = _('Project media urls')


class MemberProject(models.Model):
    class Meta:
        verbose_name = _('Member project')
        verbose_name_plural = _('Member projects')

    member = models.OneToOneField(
        to='Member', on_delete=models.CASCADE, related_name='project',
        verbose_name=_('member')
    )
    name = models.CharField(max_length=50, verbose_name=_('name'))
    description = models.TextField(
        max_length=2500, verbose_name=_('biography')
    )
    images = models.ManyToManyField(
        to='Image', blank=True, verbose_name=_('images')
    )
    tags = models.ManyToManyField(
        to='ArtistTag', blank=True, verbose_name=_('tags')
    )
    public = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def description_preview(self):
        return self.description[:DESCRIPTION_PREVIEW]
