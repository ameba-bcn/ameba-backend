from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model

from api.serializers import SingleUseTokenSerializer


User = get_user_model()


class RecoveryRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class RecoverySerializer(SingleUseTokenSerializer):
    model = User
    password = serializers.CharField(max_length=128)
    salt = settings.RECOVERY_SALT
    signature = ('id', 'email', 'password')

    def perform_action(self):
        user = self.obj
        user.set_password(self.validated_data["password"])
        user.activate()
        user.save()
