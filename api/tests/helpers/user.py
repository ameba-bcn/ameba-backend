from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group

from api.models import User


user_types = {
    'web_user': None,
    'ameba_member': None
}


def get_user(username, email, password, group_name='web_user', active=True):
    user = User.objects.create(username=username, email=email,
                               password=password)
    user.is_active = active
    user.save()
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    return user


def get_user_token(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token

