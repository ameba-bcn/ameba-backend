from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema

from api.serializers import ActivationSerializer
from api.responses import ActivationResponse
from api.signals import emails


@swagger_auto_schema(method='post', request_body=ActivationSerializer)
@api_view(['POST'])
def activate(request):
    serializer = ActivationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    emails.account_activated.send(
        sender=serializer.obj.__class__, user=serializer.obj, request=request
    )
    return ActivationResponse(username=serializer.obj.username)
