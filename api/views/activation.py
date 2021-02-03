from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt import exceptions
from rest_framework_simplejwt.settings import api_settings
from django.http import HttpResponse

from api.models import User


def my_view(request, key):
    if request.method == 'GET':
        auth = JWTAuthentication()
        try:
            validated_token = auth.get_validated_token(key)
            user_id = validated_token[api_settings.USER_ID_CLAIM]
            try:
                user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
                if not user.is_active:
                    user.activate()
                    return HttpResponse(f"Bienvenido {user.username}, "
                                        f"tu cuenta ha sido "
                                        "activada en ameba.cat")
                else:
                    return HttpResponse(f"El usuario {user.username} ya está"
                                        f" activo en ameba.cat")
            except User.DoesNotExist:
                return HttpResponse("User invalid")

        except exceptions.InvalidToken:
            return HttpResponse("Token not valid.")
