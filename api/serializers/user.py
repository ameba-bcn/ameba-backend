from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.reverse import reverse


User = get_user_model()


class UserLoginSerializer(serializers.Serializer):

    def validate_password(self, value):
        user = self.context['request'].user
        validate_password(password=value, user=user)
