from rest_framework.permissions import IsAuthenticated
from api.serializers import MemberCardSerializer, EventTicketSerializer
from api.responses import MemberCardResponse, EventTicketResponse
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from api import authentication
from api import models
from api.docs.member_card import MemberCardDocs


class EventTicketView(ListModelMixin, GenericViewSet):
    authentication_classes = (authentication.EventTicketAuthentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = MemberCardSerializer

    def list(self, request, *args, **kwargs):
        user_to_item_variant = request.user
        serializer = EventTicketSerializer(instance=user_to_item_variant)
        return EventTicketResponse(serializer.data)

    list.__doc__ = MemberCardDocs.list
