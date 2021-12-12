from django.utils.translation import gettext as _
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import hashers
from django.contrib.postgres.fields import CIEmailField

from django.utils.translation import gettext_lazy as _, gettext_noop
from django.core import signing
from django.conf import settings
from api import models as api_models


LANGUAGES = (
    ('es', gettext_noop('Spanish')),
    ('ca', gettext_noop('Catalan')),
    ('en', gettext_noop('English')),
)


class InvalidActivationToken(Exception):
    pass


class LowerCaseEmail(models.EmailField):
    def get_prep_value(self, value):
        value = super(models.EmailField, self).get_prep_value(value)
        if value is not None:
            value = value.lower()
        return value


class UserManager(models.Manager):

    def get_from_activation_token(self, activation_token):
        age = settings.ACTIVATION_EXPIRE_DAYS * 24 * 60 * 60
        act, user_id, is_active = signing.loads(activation_token, max_age=age)
        user = self.get(id=user_id)
        if (act, user_id, is_active) != ('activation', user.id, False):
            raise InvalidActivationToken
        return user


class User(AbstractUser):
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    # Fields
    first_name = None
    last_name = None
    username = models.CharField(verbose_name=_('name'), max_length=150)
    email = LowerCaseEmail(verbose_name=_('email'), unique=True)
    is_active = models.BooleanField(verbose_name=_('active'), default=False)
    language = models.CharField(
        max_length=7, choices=settings.LANGUAGES, blank=True,
        verbose_name=_('language')
    )
    # Attributes
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def cart(self):
        try:
            return self._cart
        except api_models.Cart.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self._is_password_hashed():
            self.set_password(self.password)
        return super().save(*args, **kwargs)

    def _is_password_hashed(self):
        algorithm = hashers.get_hasher().algorithm
        return self.password.startswith(algorithm)

    def has_member_profile(self):
        try:
            return self.member is not None
        except api_models.Member.DoesNotExist:
            pass
        return False

    def activate(self):
        self.is_active = True
        self.save()

    def get_activation_token(self):
        return signing.dumps(
            (self.id, self.is_active),
            salt=settings.ACTIVATION_SALT
        )

    def get_recovery_token(self):
        return signing.dumps(
            (self.id, self.email, self.password),
            salt=settings.RECOVERY_SALT
        )

    def get_event_token(self, item_variant_id):
        return signing.dumps(
            (self.id, item_variant_id),
            salt=settings.QR_EVENT_SALT
        )
