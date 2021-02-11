"""
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
