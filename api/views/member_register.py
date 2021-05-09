from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema

from api.responses import NewMemberResponse
from api.serializers import MemberRegisterSerializer


@swagger_auto_schema(method='post', request_body=MemberRegisterSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def member_register(request):
    serialized_data = MemberRegisterSerializer(data=request.data)
    serialized_data.is_valid(raise_exception=True)
    serialized_data.create(serialized_data.validated_data)
    return NewMemberResponse()
