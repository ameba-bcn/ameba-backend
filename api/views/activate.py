from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from api.serializers import ActivationSerializer


@swagger_auto_schema(method='post', request_body=ActivationSerializer)
@api_view(['POST'])
def activate(request):
    serializer = ActivationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.user.activate()
    return Response(
        status=status.HTTP_200_OK,
        data={
            'detail': f'Bienvenido {serializer.user.username}, ya puedes '
                      f'usar tu cuenta en ameba.cat'
        }
    )
