



class ProfileImagesDocs:
    common = """
# PROFILE IMAGES
EP que requiere autenticación de usuario (socio) y que admite: 
    - POST para añadir sólo una imagen al perfil del socio. 
    - GET para obtener la lista de imágenes del perfil de socio.
    - DELETE para eliminar una imagen del perfil de socio.

NOTA: El POST a este EP sólo es necesario si se quiere añadir una sola imagen al
perfil de socio, pero el flujo normal sería hacer un PATCH a /api/members/current/
con el campo `update_images` para subir todas las imágenes del perfil de una vez.

El POST debe hacerse en formato "multipart" para poder subir la imagen. La imagen 
debe estar serializada en un formato de codificación válido (jpg, png, etc).
"""
