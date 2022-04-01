

class MemberCardDocs:
    common = """

# MEMBER CARD
Endpoint authenticado para acceder directamente al carnet digital de socio con 
token.
"""

    list = """
Devuelve información del carnet de socio mediante una request simple con 
token persistente y único.

Cuando se crea un nuevo socio, éste recibe un QR en su email con una URL que apunta al front-end y con un token como queryparam:

```<site-name>/card/?token=aosidjasoidjasokdald```
Desde ésta página, el frontend tendrá que hacer una request a éste endpoint 
usando ese token en el header Authorization como Bearer token, igual que la 
authenticación normal. 
La única diferencia es que el token recibido en el QR sólo vale para acceder al carnét digital de socio y no caduca.
Sólo caduca cada vez que se genere un nuevo código QR (se invalidan todos 
los anteriores) 
"""
