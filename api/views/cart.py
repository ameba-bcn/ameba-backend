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

    def get_object(self):
        if self._is_current_user_cart(self.kwargs.get('pk')):
            current = self._get_current_user_cart(self.request.user)
            if current:
                self.kwargs['pk'] = current.pk
        return super().get_object()

    @staticmethod
    def _is_current_user_cart(pk):
        return type(pk) is str and pk == 'current'

    @staticmethod
    def _get_current_user_cart(user):
        if user.is_authenticated:
            if Cart.objects.filter(user=user).exists():
                return Cart.objects.filter(user=user)[0]
            else:
                return Cart.objects.create(user=user)
