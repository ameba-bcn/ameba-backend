from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
)
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response

from api.permissions import CartPermission
from api.serializers import CartSerializer, CheckoutSerializer
from api.models import Cart, Checkout
from rest_framework.decorators import action

CURRENT_KEY = 'current'


class CartViewSet(
    GenericViewSet, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
):
    """

    # Carrito de la compra.
    Endpoint para manipular carritos de la compra. Admite dos formas de uso,
    una autenticada y otra sin autenticar excepto para la vista `/checkout/`
    que requiere autenticación.

    La forma autenticada sirve para manipular el carrito del usuario
    autenticado y admite el reemplazo del `{id}` del carro por la etiqueta
    `'current'` en las vistas detalle ({id} en la url):

    - Siempre que se autentique la petición y se use la etiqueta `'current'`,
    se utilizará el carro correspondiente al usuario autenticado, creando
    uno nuevo en caso de que no existiese previamenete.

    - Siempre que se autentique la petición y se pase un {id} de carro que
    no pertenezca a ningún usuario, ese carro se asociará automáticamente al
    usuario autenticado.


    La forma no autenticada sirve para manipular carros de forma anónima,
    antes de que el usuario se haya autenticado y debe especificar siempre
    el {id} del carro en las vistas detalle (`{id}` en la url)

    """
    permission_classes = (CartPermission, )
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_serializer_class(self):
        if self.action == 'checkout':
            self.serializer_class = CheckoutSerializer
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
        """
        # Cart checkout
        ```python
        /api/carts/current/checkout/
        ```
        """
        cart = self.get_object()
        checkout, created = Checkout.objects.get_or_create(cart=cart)
        serializer_class = self.get_serializer_class()
        return Response(serializer_class(checkout).data)

    def partial_update(self, request, *args, **kwargs):
        """
        # Cart patch
        Modifica los items y el discount_code de un carro referenciado por
        su id. Ambos atributos son opcionales y en caso de no incluirse no
        se modifican.

        - No requiere token de autenticación (Bearer token), para lo cual hay
        que especificar un id de carro.

        - Cuando la petición se hace autenticada, acepta reemplazo del {id}
        del carro por la etiqueta 'current', de la forma:
        ```python
        /api/carts/current/checkout/
        ```
        En este caso, si el usuario no tiene carro, se crea uno nuevo.

        - Si la petición se hace autenticada, automáticamente
        se asocia el id del carro enviado al usuario al que corresponde el
        token utilizado.


        """
        return super().partial_update(request, *args, **kwargs)