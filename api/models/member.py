import datetime

from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import signing
from django.db import models
from localflavor.es.models import ESIdentityCardNumberField

from api import qr_generator
from api.models.membership import MembershipStates
import api.images as img_utils

# Get current user model
User = get_user_model()


QR_DATE_FORMAT = '%Y%m%d%H%M%S'


def get_default_number():
    if not Member.objects.all():
        return 105
    else:
        return Member.objects.all().order_by('-number').first().number + 1


def get_default_qr_date():
    return datetime.datetime.now().strftime(QR_DATE_FORMAT)


class MemberProfileImage(models.Model):
    class Meta:
        verbose_name = _('Member profile image')
        verbose_name_plural = _('Member profile images')

    member = models.ForeignKey(
        to='Member', on_delete=models.CASCADE, verbose_name=_('member'),
        related_name='images'
    )
    image = models.ImageField(
        upload_to='member_profile_images', verbose_name=_('profile image')
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )

    def __str__(self):
        return f'{self.member.user.username} profile images'

    @property
    def url(self):
        return self.image.url

    def save(self, *args, **kwargs):
        if self.image:
            img_utils.replace_image_field(self.image)
        super().save(*args, **kwargs)


class Member(models.Model):
    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')

    number = models.IntegerField(
        primary_key=True, editable=True, default=get_default_number,
        verbose_name=_('number')
    )
    user = models.OneToOneField(
        to='User', on_delete=models.CASCADE, verbose_name=_('user'),
        related_name='member'
    )
    identity_card = models.CharField(max_length=20, verbose_name='dni/nie')
    first_name = models.CharField(max_length=20, verbose_name=_('first name'))
    last_name = models.CharField(max_length=20, verbose_name=_('last name'))
    phone_number = models.CharField(
        max_length=10, verbose_name=_('phone number')
    )
    qr_date = models.CharField(max_length=14, default=get_default_qr_date)

    # Project attributes
    project_name = models.CharField(
        max_length=50, verbose_name=_('project name'), blank=True, null=True
    )
    description = models.TextField(
        max_length=2500, verbose_name=_('biography'), null=True
    )
    tags = models.ManyToManyField(
        to='ArtistTag', blank=True, verbose_name=_('tags'),
        related_name='members'
    )
    genres = models.ManyToManyField(
        to='MusicGenres', blank=True, verbose_name=_('genres'),
        related_name='members'
    )
    public = models.BooleanField(default=False)
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )
    qr = models.ImageField(upload_to='member_qr', blank=True, null=True)

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'qr_date'):
            self._original_qr_date = self.qr_date
        else:
            self._original_qr_date = None
        super().__init__(*args, **kwargs)

    def get_newest_membership(self):
        if self.memberships.all():
            return self.memberships.order_by('-expires').first()
        return None

    @property
    def is_active(self):
        if newest := self.get_newest_membership():
            return newest.is_active
        return False

    @property
    def status(self):
        if newest_membership := self.get_newest_membership():
            if newest_membership.state == MembershipStates.not_active_yet:
                return MembershipStates.active
            return newest_membership.state
        return None

    @property
    def type(self):
        if newest_membership := self.get_newest_membership():
            return newest_membership.subscription.name
        return None

    @property
    def expires(self):
        if membership := self.get_newest_membership():
            return membership.expires.strftime('%d/%m/%Y')

    def update_qr_date(self):
        self.qr_date = datetime.datetime.now().strftime(QR_DATE_FORMAT)
        self.save()

    def get_member_card_token(self):
        signature = (
            self.pk,
            self.qr_date
        )
        return signing.dumps(signature, salt=settings.QR_MEMBER_SALT)

    @property
    def qr_hash(self):
        return signing.dumps(self.number, salt=settings.QR_MEMBER_SALT)

    def regenerate_qr(self):
        if self.qr:
            self.qr.delete(save=False)
        qr_img = qr_generator.generate_member_card_qr(
            token=self.get_member_card_token(), site_name=settings.HOST_NAME
        )
        self.qr.save(f'{self.qr_hash}.png', qr_img, save=False)

    @property
    def id(self):
        return self.number

    def __str__(self):
        return f'{self.user.username} ({self.first_name[0]}. {self.last_name[0]}.)'

    def save(self, *args, **kwargs):
        if not self.number or not self.qr:
            self.regenerate_qr()
        super().save(*args, **kwargs)


class MemberMediaUrl(models.Model):
    member = models.ForeignKey(
        to='Member', on_delete=models.CASCADE, related_name='media_urls',
        verbose_name=_('Member media url')
    )
    url = models.URLField(verbose_name=_('url'))
    embedded = models.TextField(max_length=3000, blank=True)
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created')
    )

    class Meta:
        verbose_name = _('Member media url')
        verbose_name_plural = _('Member media urls')

    def __str__(self):
        return self.url
