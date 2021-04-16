

class UserDocs:

    create = """
Después de un usuario registrarse, se enviará un email de activación donde 
habrá un link a la siguiente url:

```<frontend-url>/activate/?token=<token>```

Desde esa página hay que hacer una request a éste endpoint y handlear la 
respuesta.
"""
