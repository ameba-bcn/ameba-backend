

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
"""
