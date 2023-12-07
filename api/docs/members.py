


class MembersDocs:
    common = """
# MEMBERS
Accede a la información del perfil de socio y lo edita. Utilizar siempre el
tag `current` en el lugar donde iría el id ({number}).
Ejemplo:
`/api/members/{member}/`
sería:
`/api/members/current/`

EP autenticado.
"""

    images = """
EP que admite POST para subir la imagen de usuario. También admite GET, pero es
recomendable utilizar el endpoint `/api/members/current/` para obtener la
información del perfil de socio y la imagen.

El POST debe hacerse en formato "multipart" para poder subir la imagen. La imagen 
debe estar serializada en un formato de codificación válido (jpg, png, etc).
"""
