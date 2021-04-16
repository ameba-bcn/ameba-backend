from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core import signing
from django.conf import settings
from django.shortcuts import get_object_or_404

from api.exceptions import InvalidActivationToken, ActivationTokenExpired

User = get_user_model()


class ActivationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=120)

    @staticmethod
    def validate_token(token):
        try:
            age = settings.ACTIVATION_EXPIRE_DAYS * 24 * 60 * 60
            act, user_id, is_active = signing.loads(token, max_age=age)
        except signing.SignatureExpired:
            raise ActivationTokenExpired
        except signing.BadSignature:
            raise InvalidActivationToken
        except Exception:
            raise InvalidActivationToken
        return token

    @property
    def user(self):
        return get_object_or_404(User, id=self.user_id)

    @property
    def user_id(self):
        return signing.loads(self.validated_data['token'])[1]
