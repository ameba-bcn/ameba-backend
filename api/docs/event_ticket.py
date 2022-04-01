

class EventTicket:
    common = """

# EVENT TICKET
Endpoint authenticado para acceder directamente a la entrada digital de un 
evento.
"""

    list = """
Devuelve información del evento y del nombre del usuario o socio según 
disponibilidad. Si falla, la entrada no es válida.

Cuando un usuario adquiere un evento, éste recibe un email con la entrada 
del evento. La entrada del evento es un pdf con un código QR que contiene 
una URL a:
```<site-name>/event-ticket/?token=aosidjasoidjasokdald```

En esta dirección, el frontend tendrá que hacer una GET a éste endpoint 
usando el token pasado en el header de authenticación (Authorization) como 
Bearer token, igual que la authenticación normal. 
La única diferencia es que el token recibido en el QR sólo vale para acceder al la información del evento y del usuario y no caduca.
"""
