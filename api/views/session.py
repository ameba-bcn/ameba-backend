from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import response, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken


class SessionView(TokenObtainPairView):

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return response.Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
