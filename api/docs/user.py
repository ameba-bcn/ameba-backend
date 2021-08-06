

class UserDocs:
    common = """
# USERS
Endpoint para acciones de cada user, desde el registro hasta eventos 
favoritos o perfil de socio.
"""

    create_member_profile = """
Endpoint para crear un perfil de socio al usuario logeado.
"""

    update_member_profile = """
Endpoint para modificar perfil de usuario. Se accede a través de:
"""

    create = """
Después de un usuario registrarse, se enviará un email de activación donde 
habrá un link a la siguiente url:

```<frontend-url>/activate/?token=<token>```

Desde esa página hay que hacer una request a éste endpoint y handlear la 
respuesta.

* __IMPORTANTE__: Si el POST a /users/ se hace con el parámetro opcional 
cart_id y éste id es correcto, se hará automáticamente un checkout del 
carro, por lo que este endpoint podría devolver los errores típicos del 
checkout de carro (carro vacío, subscripciones múltiples... etc)
"""
    get_member_profile = """

 Muestra datos personales del perfil de socio, así como su histórico de 
subscripciones a AMEBA.

Además hay dos atributos string con las siguientes definiciones:
- `status`: active/expired/expires_soon/None
- `type`: El nombre de alguna de las entradas en Subscriptions de la base de datos. Generalmente Socio o Pro

"""
