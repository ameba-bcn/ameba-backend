from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group

import api.models as api_models
import api.tests.helpers.items as item_helpers

user_types = {
    'web_user': None,
    'ameba_member': None
}


def get_user(username, email, password, group_name='web_user', active=True):
    user = api_models.User.objects.create(username=username, email=email,
                               password=password)
    user.is_active = active
    user.save()
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    return user


def get_user_token(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


def get_member(
    user=None,
    identity_card='55555555M',
    first_name='Member',
    last_name='Frito',
    phone_number='666666666'
):
    if not user:
        user = get_user(username='Namerandom', email='random@email.com',
                 password='12345')

    return api_models.Member.objects.create(
        user=user,
        identity_card=identity_card,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number
    )


