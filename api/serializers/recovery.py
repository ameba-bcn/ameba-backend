from rest_framework import serializers
from django.conf import settings

from api.serializers import SingleUseTokenSerializer


class RecoveryRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class RecoverySerializer(SingleUseTokenSerializer):
    password = serializers.CharField(max_length=128)
    salt = settings.RECOVERY_SALT
    signature = ('id', 'email', 'password')

    def perform_action(self):
        user = self.user
        user.set_password(self.validated_data["password"])
        user.activate()
        user.save()
