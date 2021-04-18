from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import response, status, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema

from api.serializers import DeleteTokenSerializer
from api.signals.emails import user_registered
from api.exceptions import WrongProvidedCredentials

User = get_user_model()


class TokenView(TokenObtainPairView):

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

    @swagger_auto_schema(request_body=DeleteTokenSerializer)
    def delete(self, request, token, **kwargs):
        data = {'refresh': token}
        serializer = self.get_serializer(request.user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except AuthenticationFailed:
            if User.objects.filter(email=request.data.get('email')):
                user = User.objects.get(email=request.data.get('email'))
                if user.check_password(request.data.get('password')):
                    user_registered.send(
                        sender=User, user=user, request=request
                    )
            raise WrongProvidedCredentials
