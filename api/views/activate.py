from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from api.serializers import ActivationSerializer


@api_view(['GET'])
def activate(request):
    serializer = ActivationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.user.activate()
    return Response(status=status.HTTP_200_OK)
