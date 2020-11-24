from django.contrib.auth import get_user_model
from rest_framework import serializers

# Get current user model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(read_only=True)
    is_active = serializers.BooleanField(required=False)
    date_joined = serializers.DateTimeField(required=False)

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = [
            'username', 'password', 'email', 'member', 'is_active', 'date_joined'
        ]

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
