from django.contrib.auth import get_user_model
from rest_framework import serializers

# Get current user model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'member', 'is_active', 'date_joined']
