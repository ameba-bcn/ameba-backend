from django.core import exceptions
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import hashers
from django.utils.translation import ugettext_lazy as _
from django.core import signing
from django.conf import settings

from api import models as api_models


class InvalidActivationToken(Exception):
    pass


class UserManager(models.Manager):

    def get_from_activation_token(self, activation_token):
        age = settings.ACTIVATION_EXPIRE_DAYS * 24 * 60 * 60
        user_id, is_active = signing.loads(activation_token, max_age=age)
        user = self.get(id=user_id)
        return user


class User(AbstractUser):
    # Fields
    first_name = None
    last_name = None
    username = models.CharField(_('name'), max_length=150)
    email = models.EmailField(_('email'), unique=True)
    is_active = models.BooleanField(_('active'), default=False)
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
        try:
            member = api_models.Member.objects.get(email=self.email)
            self.member = member
        except exceptions.ObjectDoesNotExist:
            pass
        return super().save(*args, **kwargs)

    def _is_password_hashed(self):
        algorithm = hashers.get_hasher().algorithm
        return self.password.startswith(algorithm)

    def is_member(self):
        return api_models.Member.objects.filter(user=self.id).exists()

    def activate(self):
        self.is_active = True
        self.save()

    def get_activation_token(self):
        return signing.dumps((self.id, self.is_active))
