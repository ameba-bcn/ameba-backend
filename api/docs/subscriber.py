

class SubscriberDocs:
    common = """
# SUBSCRIBE

Endpoint para subscribir email a newsletter.

```<domain>/api/subscribe/```

Este endpoint se puede usar apra suscribir emails directamente desde la web, o a través del link que aparece en los emails. 
Cuando se envía un email con un botón de "SUBSCRIBE", la url del botón apunta a la dirección:
```<domain>/subscribe/?email=<user_email>```
con el queryparam ```email```. El frontend tiene que parsear el queryparam y hacer POST al endpoint pasando el email al body.
```
POST - <domain>/api/subscribe/
body - {"email": "<email>"}
```
- Luego tendrá que mostrar el mensaje de la respuesta al usuario:
```
response 200 -> {'detail': 'bla bla bla'}
```
"""
