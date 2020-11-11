from django.db import models
from django.contrib.auth.models import User as AuthUser

from api.models.member import Member


class User(AuthUser):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)

