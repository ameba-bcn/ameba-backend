from api.serializers import DeleteTokenSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import response, status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import mixins


class SessionView(TokenObtainPairView, mixins.DestroyModelMixin):

    def get_serializer_class(self):
        if self.request.method == 'DELETE':
            self.serializer_class = DeleteTokenSerializer
        return super().get_serializer_class()

    def get_authenticators(self):
        if self.request.method == 'DELETE':
            self.authentication_classes = [JWTAuthentication]
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
