from django.contrib.auth.models import User
from django.db import models
from api.models.membership import Membership
from api.models.address import Address


class Member(models.Model):
    number = models.IntegerField(primary_key=True)
    memberships = models.ManyToManyField(Membership)
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, related_name='member'
    )
    email = models.EmailField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=10)

