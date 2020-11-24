from django.contrib.auth import get_user_model
from rest_framework import viewsets

from api.serializers.user import UserSerializer

# Get current user model
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
