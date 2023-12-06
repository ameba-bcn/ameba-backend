from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models


DESCRIPTION_PREVIEW = 160


class MemberProjectMediaUrl(models.Model):
    member = models.ForeignKey(
        to='MemberProject', on_delete=models.CASCADE, related_name='media_urls',
        verbose_name=_('artist')
    )
    url = models.URLField(verbose_name=_('url'))
    embedded = models.TextField(max_length=2000, blank=True)
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )

    class Meta:
        verbose_name = _('Project media url')
        verbose_name_plural = _('Project media urls')

    def __str__(self):
        return self.url


class MemberProject(models.Model):
    class Meta:
        verbose_name = _('Member project')
        verbose_name_plural = _('Member projects')

    member = models.OneToOneField(
        to='Member', on_delete=models.CASCADE, related_name='project',
        verbose_name=_('member'), primary_key=True
    )
    name = models.CharField(max_length=50, verbose_name=_('name'))
    description = models.TextField(
        max_length=2500, verbose_name=_('biography')
    )
    image = models.ImageField(
        upload_to='member_projects', verbose_name=_('image')
    )
    tags = models.ManyToManyField(
        to='ArtistTag', blank=True, verbose_name=_('tags')
    )
    public = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def id(self):
        return self.member.id
