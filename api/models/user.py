from django.db import models
from django.contrib import auth

from api.models.address import Address
from api.models.membership import Membership


class User(auth.get_user_model()):
    membership = models.OneToOneField(
        to=Membership, to_field=Membership.number, on_delete=models.CASCADE
    )
    address = models.OneToOneField(to=Address, on_delete=models.CASCADE)

