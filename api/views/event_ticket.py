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
    serializer_class = EventTicketSerializer

    def list(self, request, *args, **kwargs):
        user_to_item_variant = request.instance
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=user_to_item_variant)
        return EventTicketResponse(serializer.data)


    list.__doc__ = MemberCardDocs.list
