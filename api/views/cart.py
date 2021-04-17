from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from api.permissions import CartPermission
from api.serializers import CartSerializer, CartCheckoutSerializer
from api.models import Cart
from api.exceptions import CartIsEmpty, CartCheckoutNeedsUser
from api.signals import cart_checkout, cart_processed
from api.docs.carts import CartsDocs

CURRENT_LABEL = 'current'


class CartViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin,
                  DestroyModelMixin, CreateModelMixin):
    permission_classes = (CartPermission, )
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_serializer_class(self):
        if self.action == 'checkout':
            self.serializer_class = CartCheckoutSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'checkout':
            self.permission_classes = (CartPermission, IsAuthenticated)
        return super().get_permissions()

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(request.method)
        return super().update(request, *args, **kwargs)

    def get_object(self):
        if self._is_current_label_id(self.kwargs.get('pk')):
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
    def _is_current_label_id(pk):
        return type(pk) is str and pk == CURRENT_LABEL

    @staticmethod
    def _get_current_user_cart(user):
        if user.is_authenticated:
            return Cart.objects.get_or_create(user=user)[0]
        raise NotAuthenticated

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        cart = self.get_object()
        cart_processed.send(sender=self, cart=cart, request=self.request)
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['GET'])
    def checkout(self, request, *args, **kwargs):
        cart = self.get_object()
        if cart.is_empty():
            raise CartIsEmpty
        if cart.is_anonymous():
            raise CartCheckoutNeedsUser
        cart_checkout.send(sender=self, cart=cart, request=self.request)
        serializer_class = self.get_serializer_class()
        return Response(serializer_class(cart).data)

    # Documentation
    partial_update.__doc__ = CartsDocs.partial_update
    checkout.__doc__ = CartsDocs.checkout
    destroy.__doc__ = CartsDocs.destroy
    retrieve.__doc__ = CartsDocs.retrieve
