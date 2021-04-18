from rest_framework import serializers
from django.conf import settings

from api.serializers import SingleUseTokenSerializer


class RecoveryRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(read_only=True)


class RecoverySerializer(SingleUseTokenSerializer):
    password = serializers.CharField(max_length=128)
    salt = settings.RECOVERY_SALT
    signature = ('id', 'email', 'password')

    def perform_action(self):
        self.user.set_password(self.password)
