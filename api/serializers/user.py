from django.contrib.auth import get_user_model
from rest_framework import serializers

# Get current user model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(read_only=True)
    date_joined = serializers.DateTimeField(required=False)

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = [
            'username', 'password', 'email', 'member', 'date_joined'
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs
