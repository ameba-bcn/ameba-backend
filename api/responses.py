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
    message = '¡Password cambiado!'


class RecoveryResponse(Response):
    message = 'Si {email} se encuentra en nuestra base de datos, ' \
              'enviaremos un link para reestablecer la contraseña.'

    def __init__(self, email):
        super().__init__(
            status=status.HTTP_200_OK,
            data=dict(detail=self.message.format(email=email))
        )


class NewSubscriberResponse(Response):
    message = 'Gracias por suscribirte a la newsletter de AMEBA.'

    def __init__(self):
        super().__init__(
            status=status.HTTP_200_OK,
            data=dict(detail=self.message)
        )


class NewMemberResponse(Response):
    def __init__(self):
        super().__init__(
            status=status.HTTP_201_CREATED
        )
