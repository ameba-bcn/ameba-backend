from django.core import exceptions
from django.contrib.auth import get_user_model
from django.db import models
from api.models.membership import Membership
from api.models.address import Address


# Get current user model
User = get_user_model()


class Member(models.Model):
    member = models.IntegerField(primary_key=True)
    memberships = models.ManyToManyField(Membership, blank=True)
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, related_name='member',
        blank=True, null=True
    )
    email = models.EmailField()
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        try:
            user = User.objects.get(email=self.email)
            self.user = user
        except exceptions.ObjectDoesNotExist:
            pass
        super().save(*args, **kwargs)

    def is_user(self):
        return self.user is not None
