from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema

from api.responses import NewMemberResponse
from api.serializers import MemberRegisterSerializer
from api.signals import user_registered
from api.models import User


@swagger_auto_schema(method='post', request_body=MemberRegisterSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def member_register(request):
    serialized_data = MemberRegisterSerializer(data=request.data)
    serialized_data.is_valid(raise_exception=True)
    member_profile = serialized_data.create(serialized_data.validated_data)
    user = member_profile.user
    user_registered.send(sender=User, user=user, request=request)
    return NewMemberResponse()
