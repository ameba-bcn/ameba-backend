import random
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from django.core.files.images import ImageFile

import api.models as api_models
import api.tests.helpers.items as item_helpers

user_types = {
    'web_user': None,
    'ameba_member': None
}

chiquito_ipsum = 'Lorem fistrum pecador te va a hasé pupitaa sexuarl papaar papaar jarl ahorarr condemor ahorarr. Al ataquerl a peich qué dise usteer te va a hasé pupitaa ese pedazo de. Ese hombree ese que llega papaar papaar pecador caballo blanco caballo negroorl ese pedazo de al ataquerl. Al ataquerl jarl mamaar pupita condemor torpedo. Te voy a borrar el cerito ahorarr te va a hasé pupitaa mamaar de la pradera ese pedazo de torpedo hasta luego Lucas sexuarl caballo blanco caballo negroorl por la gloria de mi madre. Condemor papaar papaar ese hombree está la cosa muy malar se calle ustée.'


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
    phone_number='666666666',
    public=False
):
    if not user:
        while True:
            try:
                i = random.randint(0, 1000)
                user = get_user(
                    username=f'Username{i}', email=f'username{i}@email.com',
                    password='12345'
                )
                break
            except Exception as e:
                pass

    return api_models.Member.objects.create(
        user=user,
        identity_card=identity_card,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        public=public
    )

