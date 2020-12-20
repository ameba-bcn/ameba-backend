from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions as drf_permissions

from api import serializers
from api import permissions

# Get current user model
User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.CustomModelUserPermission]

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [drf_permissions.AllowAny]
        return super().get_permissions()

    def get_object(self):
        if self._is_current_user(self.kwargs.get('pk')):
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object()

    @staticmethod
    def _is_current_user(pk):
        return type(pk) is str and pk == 'current'
