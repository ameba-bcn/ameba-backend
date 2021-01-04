from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny

from api.serializers import CartSerializer
from api.models import Cart


class CartViewSet(
    GenericViewSet, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
):
    serializer_class = CartSerializer

