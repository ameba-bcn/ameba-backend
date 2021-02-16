from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
)
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from api.permissions import CartPermission
from api.serializers import CartSerializer, CartCheckoutSerializer
from api.models import Cart
from api.exceptions import CartIsEmpty
from api.signals import cart_checkout

CURRENT_KEY = 'current'


class CartViewSet(
    GenericViewSet, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin,
    DestroyModelMixin
):
    permission_classes = (CartPermission, )
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_serializer_class(self):
        if self.action == 'checkout':
            self.serializer_class = CartCheckoutSerializer
        return super().get_serializer_class()

    def get_object(self):
        if self._is_current_user_cart(self.kwargs.get('pk')):
            current = self._get_current_user_cart(self.request.user)
            self.kwargs['pk'] = current.pk
        cart = super().get_object()
        self.resolve_user(cart)
        return cart

    def resolve_user(self, cart):
        user = self.request.user
        if user.is_authenticated and cart.user != self.request.user:
            if user.cart:
                user.cart.delete()
            cart.user = self.request.user
            cart.save()

    @staticmethod
    def _is_current_user_cart(pk):
        return type(pk) is str and pk == CURRENT_KEY

    @staticmethod
    def _get_current_user_cart(user):
        if user.is_authenticated:
            return Cart.objects.get_or_create(user=user)[0]
        raise NotAuthenticated

    @action(detail=True, methods=['GET'])
    def checkout(self, request, *args, **kwargs):
        cart = self.get_object()
        if cart.is_empty():
            raise CartIsEmpty
        cart_checkout.send(sender=self, cart=cart, request=self.request)
        serializer_class = self.get_serializer_class()
        return Response(serializer_class(cart).data)
