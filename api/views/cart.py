from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
)
from rest_framework.permissions import AllowAny

from api.serializers import CartDetailSerializer, CartWriteSerializer
from api.models import Cart


class CartViewSet(
    GenericViewSet, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
):
    permission_classes = (AllowAny, )
    serializer_class = CartDetailSerializer
    queryset = Cart.objects.all()
    lookup_field = 'hash'

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            self.serializer_class = CartWriteSerializer
        return super().get_serializer_class()
