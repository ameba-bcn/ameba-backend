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
        """ Obtiene el resumen para continuar con el pago. En caso de que sea
        la primera vez que se  hace checkout para un carrito, se establecerá
        en este momento la primera  interación con la pasarela de pagos creando
        un PaymentIntent que gestionará el estado del pago durante el proceso.
        Para hacer checkout de un carrito,  el carrito tiene que contener  al
        menos 1 artículo.

        El flujo de checkout está basado en  https://stripe.com/docs/payments/integration-builder
        seleccionando "Web", "HTML", "Python" y "Custom Payment Method".

        Aquí he usado HTML para implementar una demo, aunque en  la web
        debería ser React en lugar de HTML.

        ## Prueba del flujo completo

        Login con:
        ```
        web_user@ameba.cat
        ameba12345
        ```

        Añade items a un carro, y abre en el navegador la página:
        ```/carts/current/checkout/client/```

        Luego introduce uno de los siguientes valores de tarjeta de crédito:
        ```
        Payment succeeds:
            4242 4242 4242 4242
            08/24
            123
            08017
        Authentication required
            4000 0025 0000 3155
            08/24
            123
            08017
        Payment is declined
            4000 0000 0000 9995
            08/24
            123
            08017
        ```

        Al hacer click el pago ficticio se procesa y si el resultado es ok,
        el carro debería resetearse y una nueva entrada aparecer en
        la sección Payments del admin panel del backend.

        ## Implementación
        En primer lugar, para test, hay que configurar la clave pública de
        stripe, que para hacer tests en nuestro caso podemos  usar la siguiente:
        ```
        var stripe = Stripe("pk_test_51IGkXjHRg08Ncmk7fPlbb9DfTF5f7ckXBKiR4g01euLgXs04CqmgBPOQuqQfOhc6aj9mzsYE1oiQ3TFjHH9Hv3Mj00GNyG9sep");
        ```

        A countinuación, el script llama al endpoint /create-payment-intent:
        ```
        fetch("/create-payment-intent", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(purchase)
        })
        ```

        En nuestro caso éste endpoint (/api/carts/current/checkout/), tipo:
        ```
        fetch("/api/carts/current/checkout/", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token.access
          },
        })
        ```

        Este endpoint  devuelve en la respuesta un resumen del pago de la
        siguiente forma:
        ```
        response = {
            "user": 1,
            "email": "web_user@ameba.cat",
            "total": "90.00 €",
            "amount": 9000,
            "cart_items": {...},
            "checkout":  {
                "client_secret": "soaidhasldksjasfjsodisaljkdoasidja"
            }
        }
        ```

        En la  respuesta, el client_secret equivaldría al clientSecret del
        script client.js, así que habría que sustituir la parte de
        ```
        payWithCard(stripe, card, data.clientSecret);
        ``` por: ```
        payWithCard(stripe, card, data.checkout.client_secret);
        ```
        Por último, una vez se ha intentado procesar el  pago, hay que
        handlear la respuesta y en caso que sea ok, hacer un DELETE al
        respuesta, endpoint `/carts/current/` con el mismo usuario autenticado.
        ```javascript
        .then(function(result) {
          if (result.error) {
            // Handlear mensaje de error aquí!!!!
            showError(result.error.message);
          } else {
              orderComplete(result.paymentIntent.id);
              // The payment succeeded!
              // Si  el pago es ok, DELETE http://localhost:8000/api/carts/current/
              // autenticado.
              fetch("/api/carts/current/", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token.access
                },
              })
                .then(response => response.text())
                .then(result => console.log(result))
                .catch(error => console.log('error', error));
          }
        });
        ```
        """
        cart = self.get_object()
        if cart.is_empty():
            raise CartIsEmpty
        cart_checkout.send(sender=self, cart=cart, request=self.request)
        serializer_class = self.get_serializer_class()
        return Response(serializer_class(cart).data)
