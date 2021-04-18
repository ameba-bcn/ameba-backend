from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

from api.serializers import RecoverySerializer, RecoveryRequestSerializer
from api.signals.emails import account_recovery, password_changed
from api.responses import RecoveryRequestResponse, RecoveryResponse
from api.docs.recovery import RecoveryDocs

User = get_user_model()


class RecoveryViewSet(GenericViewSet):
    __doc__ = RecoveryDocs.__doc__
    serializer_class = RecoveryRequestSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            self.serializer_class = RecoverySerializer
        return super().get_serializer_class()

    @swagger_auto_schema(responses={200: ''})
    def create(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password_changed.send(sender=User, user=serializer.user,
                              request=request)
        return RecoveryRequestResponse(username=serializer.user.username)

    @swagger_auto_schema(responses={200: ''}, query_serializer=RecoveryRequestSerializer)
    def list(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.query_params)
        serializer.is_valid()
        email = serializer.validated_data['email']
        if User.objects.filter(email=email):
            user = User.objects.get(email=email)
            account_recovery.send(sender=User, user=user, request=request)
        return RecoveryResponse(email=email)

