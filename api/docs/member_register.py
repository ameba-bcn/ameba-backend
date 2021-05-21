

class MemberRegisterDocs:
    common = """
# MEMBER REGISTER

Endpoint para registrar un usuario en el proceso de nueva subscripción. 
Incluye los datos de usuario y de perfil de socio, además de un 
identificador de carro.

* __IMPORTANTE__: Este endpoint hará automáticamente un checkout del 
carro, por lo que podría devolver en caso de que hubiera, los errores 
típicos del checkout de carro (carro vacío, subscripciones múltiples... etc)

"""
