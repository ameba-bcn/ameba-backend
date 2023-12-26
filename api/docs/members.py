


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

El perfil de socio se edita haciendo un PATCH a este endpoint con los campos 
que se quieren cambiar. 

- El campo `update_images` es un campo especial (array de imágenes) para subir 
las imágenes del perfil. Si el campo no se envía, no se suben imágenes. 
Si se envía, se sobreescriben las imágenes que hubiera en el perfil. 
Al subir imágenes, se debe hacer en formato "multipart" para poder subir 
la imagen. La imagen debe estar serializada en un formato de codificación 
válido (jpg, png, etc).

- El campo `genres` es un array de strings con los géneros musicales que
le gustan al socio. Si el campo no se envía, no se actualizan los géneros.
El campo es libre, y cuando se envía, se comprueba que los géneros existan
en la base de datos. Si no existen, se crean. Para mostrar al usuario una lista
de generos existentes o implementar una función de autocompletado, se puede hacer 
un GET a `/api/genres/`. Este EP devolverá los géneros que hayan subido otros 
usuarios y se hayan validado manualmente en el panel de administración activando 
el campo `validated` en el modelo `MusicGenres`.
"""
