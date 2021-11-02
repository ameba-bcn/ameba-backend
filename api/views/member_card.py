from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema

from api.serializers import MemberCardSerializer
from api.responses import MemberCardResponse
from api.signals import emails


@swagger_auto_schema(method='get', request_body=MemberCardSerializer)
@api_view(['GET'])
def member_card(request):
    serializer = MemberCardSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return MemberCardResponse(serializer.data)
