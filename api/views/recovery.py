from rest_framework import generics
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model

from api.serializers import RecoverySerializer, RecoveryRequestSerializer
from api.signals.emails import account_recovery

User = get_user_model()


class RecoveryViewSet(GenericViewSet):
    serializer_class = RecoveryRequestSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            self.serializer_class = RecoverySerializer
        return super().get_serializer_class()

    def create(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            status=status.HTTP_200_OK,
            data={
                'detail': f'Bienvenido {serializer.user.username}, ya puedes '
                          f'usar tu cuenta en ameba.cat'
            }
        )

    def list(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.query_params)
        serializer.is_valid()
        email = serializer.validated_data['email']
        if User.objects.filter(email=email):
            user = User.objects.get(email=email)
            account_recovery.send(sender=User, user=user, request=request)
        return Response(
            status=status.HTTP_200_OK,
            data={
                'detail': f'Si {email} se encuentra en nuestra base de datos, '
                          f'enviaremos un link para reestablecer la '
                          f'contraseña.'
            }
        )
