from rest_framework.response import Response
from rest_framework import status


class ActivationResponse(Response):
    message = 'Bienvenido {username}, ya puedes usar tu cuenta de AMEBA.'

    def __init__(self, username):
        super().__init__(
            status=status.HTTP_200_OK,
            data=dict(detail=self.message.format(username=username))
        )


class RecoveryRequestResponse(ActivationResponse):
    message = 'Bienvenido {username}, ya puedes usar tu cuenta en ameba.cat'


class RecoveryResponse(Response):
    message = 'Si {email} se encuentra en nuestra base de datos, ' \
              'enviaremos un link para reestablecer la contraseña.'

    def __init__(self, email):
        super().__init__(
            status=status.HTTP_200_OK,
            data=dict(detail=self.message.format(email=email))
        )
