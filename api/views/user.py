from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers.user import UserSerializer

# Get current user model
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        if type(kwargs.get('pk')) is str and kwargs.get('pk') == 'current':
            instance = request.user
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        return super().retrieve(request, *args, **kwargs)
