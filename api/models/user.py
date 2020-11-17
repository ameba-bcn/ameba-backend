from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    # Fields
    first_name = None
    last_name = None
    username = models.CharField(_('name'), max_length=150)
    email = models.EmailField(_('email'), unique=True)

    # Attributes
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
