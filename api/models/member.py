from django.core import exceptions
from django.contrib.auth import get_user_model
from django.db import models
from api.models.membership import Membership


# Get current user model
User = get_user_model()


def get_default_number():
    if not Member.objects.all():
        return 100
    else:
        return Member.objects.all().order_by('-number').first().number + 1


class Member(models.Model):
    number = models.IntegerField(primary_key=True, editable=True,
                                 default=get_default_number)
    user = models.OneToOneField(to='User', on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=10)

    @property
    def active_membership(self):
        if self.memberships.all():
            return not self.memberships.order_by('-expires').first().is_expired
        return None
