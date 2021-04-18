

class ActivateDocs:
    common = """
# ACTIVATE

Endpoint para flujo de activación de cuenta.
- Cuando se crea un usuario nuevo, este por defecto no está activo, pero se 
le envía un email con un link de la siguiente forma:
```<domain>/activate/?token=<token>```
- El frontend tendrá que parsear el queryparam en la página /activate/ y 
hacer una request al backend:
```
POST - <domain>/api/activate/
body - {"token": "<token>"}
```
- Luego tendrá que mostrar el mensaje de la respuesta al usuario:
```
response 200 -> {'detail': 'bla bla bla'}
```
"""
