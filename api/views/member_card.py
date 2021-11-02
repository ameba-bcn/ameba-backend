from rest_framework.permissions import IsAuthenticated
from api.serializers import MemberCardSerializer
from api.responses import MemberCardResponse
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from api import authentication
from api import models
from api.docs.member_card import MemberCardDocs


class MemberCard(ListModelMixin, GenericViewSet):
    authentication_classes = (authentication.MemberCardAuthentication, )
    permission_classes = (IsAuthenticated, )
    model = models.Member
    serializer_class = MemberCardSerializer

    def list(self, request, *args, **kwargs):
        member = request.user.member
        serializer = MemberCardSerializer(instance=member)
        return MemberCardResponse(serializer.data)

    list.__doc__ = MemberCardDocs.list
