from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import AllowAny

from api.serializers import FullRegistrationSerializer


class FullRegistrationViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    serializer_class = FullRegistrationSerializer
    permission_classes = (AllowAny, )
