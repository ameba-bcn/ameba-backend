from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

from api.serializers import SingleUseTokenSerializer

User = get_user_model()


class MemberCardSerializer(SingleUseTokenSerializer):
    token = serializers.CharField(max_length=120, required=True)
    signature = ('id', 'is_active')
    salt = settings.ACTIVATION_SALT
