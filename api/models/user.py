from django.core import exceptions
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import hashers
from django.utils.translation import ugettext_lazy as _

from api import models as api_models


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

    @property
    def membership(self):
        return [m for m in self.memberships.filter(is_active=True)]
