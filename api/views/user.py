from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins
from rest_framework import permissions as drf_permissions

from api import serializers
from api import permissions
from api.signals import user_registered
from api.docs.user import UserDocs

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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(email=request.data['email'])
            user_registered.send(sender=User, user=user, request=request)
        return response

    create.__doc__ = UserDocs.create