from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
)
from api.permissions import CartPermission
from api.serializers import CartSerializer
from api.models import Cart


class CartViewSet(GenericViewSet, RetrieveModelMixin, CreateModelMixin,
                  UpdateModelMixin):
    permission_classes = (CartPermission, )
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
