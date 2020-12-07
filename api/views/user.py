from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers.user import UserSerializer

# Get current user model
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        if self._is_current_user(self.kwargs.get('pk')):
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object()

    @staticmethod
    def _is_current_user(pk):
        return type(pk) is str and pk == 'current'
