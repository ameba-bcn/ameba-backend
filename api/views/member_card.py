from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from api.serializers import MemberCardSerializer
from api.responses import MemberCardResponse
from api.views.base import BaseReadOnlyViewSet
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from api import authentication
from api import models

@swagger_auto_schema(method='post', request_body=MemberCardSerializer)
@api_view(['POST'])
@authentication_classes((authentication.MemberCardAuthentication, ))
@permission_classes((IsAuthenticated, ))
def member_card(request):
    member = request.user.member
    serializer = MemberCardSerializer(instance=member)
    return MemberCardResponse(serializer.data)


class MemberCard(ListModelMixin, GenericViewSet):
    authentication_classes = (authentication.MemberCardAuthentication, )
    permission_classes = (IsAuthenticated, )
    model = models.Member
    serializer_class = MemberCardSerializer

    def list(self, request, *args, **kwargs):
        member = request.user.member
        serializer = MemberCardSerializer(instance=member)
        return MemberCardResponse(serializer.data)
