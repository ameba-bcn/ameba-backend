from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from api import models
from api import exceptions

# Get current user model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(read_only=True)
    date_joined = serializers.DateTimeField(required=False)
    cart_id = serializers.CharField(
        max_length=64, write_only=True, required=False
    )

    class Meta:
        model = User
        extra_kwargs = {
            'password': {'write_only': True}
        }
        fields = [
            'username', 'password', 'email', 'member', 'date_joined', 'cart_id'
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

    def create(self, validated_data):
        cart_id = validated_data.pop('cart_id', None)
        user = super().create(validated_data)
        if models.Cart.objects.filter(id=cart_id):
            cart = models.Cart.objects.get(id=cart_id)
            cart.user = user
            cart.save()
        elif cart_id:
            raise exceptions.WrongCartId
        return user
