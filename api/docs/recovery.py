

class RecoveryDocs:
    common = """
# RECOVERY

Endpoint para flujo de recuperación de cuenta (password reset).
- Para hacer una request de recuperación de cuenta:
```GET - <domain>/api/recovery/?email=<email>```
- Para resetear password, en el email se adjunta un link del tipo:
```<domain>/recovery/?token=<token>```
Esta página tendrá que parsear el queryparam, obtener el token y hacer:
```
POST - <domain>/api/recovery/
body - {"token": "<token>"}
```
- Luego tendrá que mostrar el mensaje de la respuesta al usuario:
```
response 200 -> {'detail': 'bla bla bla'}
"""
