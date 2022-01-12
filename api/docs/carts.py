

class CartsDocs:
    common = """
# CARTS

Endpoints para manipular carritos de la compra. Admiten dos formas de uso,
una autenticada y otra sin autenticar excepto para el endpoint `/checkout/`,
que requiere autenticación.

La forma **autenticada** sirve para manipular el carrito del usuario
autenticado y admite el reemplazo del `{id}` del carro por la etiqueta
`'current'` en las vistas detalle (del tipo `carts/{id}/`):

- Siempre que se autentique la petición y se use la etiqueta `'current'`,
se utilizará el carro correspondiente al usuario autenticado, creando
uno nuevo en caso de que no existiese previamenete.

- Siempre que se autentique la petición y se pase un {id} de carro que
no pertenezca a ningún usuario, ese carro se asociará automáticamente al
usuario autenticado.

    _**-->> Esta acción borrará permanentemente cualquier carro
    anterior que hubiese asociado al usuario autenticado!!**_


La forma **no autenticada** sirve para manipular carros de forma anónima,
antes de que el usuario se haya autenticado y debe especificar siempre
el {id} del carro en las vistas detalle (del tipo `carts/{id}/`)
"""

    partial_update = """
Actualiza los elementos del carrito mediante la lista "item_variant_ids" del body:
```
{
    "item_variant_ids": [1, 3, 4]
}
```
Los item_variant_ids son los ids de la lista de __"variants"__ que aparecen en 
la respuesta de alguno de los siguientes endpoints:
```
/articles/<id>/ 
/events/<id>/ 
/subscriptions/<id>/
```
### Forma autenticada (con  bearer token):
- Se puede reemplazar el id del carro en la url por la etiqueta 
"current" `/api/carts/current/`
- Si el usuario autenticado no tiene ningún carro, se crea uno
automágicamente.

### Forma no autenticada (sin bearer token):
- Hay que saber el id del carro previamente e incluirlo en la url.

Si la lista items está vacía se vacía el carro. Si no se pasa la key
"item_variant_ids" no hace nada.
"""

    checkout = """
Obtiene el resumen para continuar con el pago. 
Para hacer checkout de un carrito,  el carrito tiene que contener  al menos 
1 artículo.
Cada vez que se modifique el carro, hay que hacer un checkout antes de 
finalizar el proceso de pago.
"""

    payment = """
Para comenzar el pago hay que hacer un GET a este este endpoint. 
El endpoint devuelve el "status", el "payment_intent_id" y el 
"client_secret" para utilizarlos en el formulario de pago.

- __Requiere autenticación__ de usuario y admite reemplazo del id del carro  
por la etiqueta "current".

"""

    retrieve = """
Obtiene un carro y su información a  través del id pasado en la url.
### Forma autenticada (con  bearer token):
- Se puede reemplazar el id del carro en la url por la etiqueta 
"current" `/api/carts/current/`
- Si el usuario autenticado no tiene ningún carro, se crea uno
automágicamente.

### Forma no autenticada (sin bearer token):
- Hay que saber el id del carro previamente e incluirlo en la url.


### Atributo "state" del carro
El estado del carro es un diccionario no almacenado que se computa 
dinámicamente "on the fly". De esta forma siempre está actualizado y sólo 
depende de variables internas del carro. Este estado debe contener toda la 
información necesaria para implementar cualquier flujo de carro en el frontend.
La estructura del diccionario es:
```
"state" = {
    "has_user": <bool>,
    "has_member_profile": <bool>,
    "has_memberships": <integer>,
    "has_articles": <integer>,
    "has_events": <integer>,
    "has_subscriptions": <bool>,
    "needs_checkout": <bool>
}
```

Significado de cada atributo de estado:

- __has_user__: indica si el carro está asociado a un usuario o es anónimo.
- __has_member_profile__: en caso de tener usuario asociado, indica si el 
usuario tiene un perfil de socio o no.
- __has_memberships__: indica si el usuario es o ha sido miembro de la 
asociación en algún momento. Implicaría que las dos anteriores son true.
- __has_articles__: indica si el carro tiene items del tipo article (tienda).
- __has_events__: indica si el carro tiene items del tipo event (agenda).
- __has_subscriptions__: indica si el carro tiene items del tipo subscripción (
socios)
- __needs_checkout__: indica si el carro necesita checkout antes de finalizar 
el proceso de compra o no. Este valor será true cuando nunca se ha hecho un checkout o cuando se han modificado los artículos del carro.

De esta forma, se pueden usar los atributos en flujos de compra para saber 
el estado del flujo después del login. Por ejemplo:

- `needs_checkout==false && has_subscriptions==1 && has_memberships==False` 
indica que el usuario ha iniciado un proceso de compra, ya que ha hecho 
checkout, y que el proceso pertenece a una subscripción nueva, ya que no 
tiene ni ha tenido memberships.
- `needs_checkout==false && has_subscriptions==1 && has_memberships==True` 
como en el ejemplo anterior pero en este caso siendo una renovación de 
socio, ya que el usuario tiene o ha tenido memberships. 
- `needs_checkout==false && has_article==1` 
indica que el usuario ha iniciado un proceso de compra, ya que ha hecho 
checkout, y que el proceso pertenece a compra de articulos de la tienda.

El hecho de que por ejemplo coexistan `has_article > 0 && has_subscriptions > 0` dependerá de cómo el frontend gestione los flujos de compra de los 
diferentes tipos.

"""
