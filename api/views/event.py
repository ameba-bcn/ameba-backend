from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, DestroyModelMixin, CreateModelMixin, RetrieveModelMixin
)
from rest_framework.permissions import IsAuthenticated

from api.serializers import EventListSerializer, EventDetailSerializer, \
    UserSavedEventsListSerializer
from api.models import Event, ItemVariant
from api.views.base import BaseReadOnlyViewSet


class EventViewSet(BaseReadOnlyViewSet):
    list_serializer = EventListSerializer
    detail_serializer = EventDetailSerializer
    model = Event
    queryset = Event.objects.filter(is_active=True).order_by('-datetime')\
        .prefetch_related('variants', 'discounts', 'images', 'type')


class UserSavedEventsViewSet(CreateModelMixin, DestroyModelMixin,
                             ListModelMixin, GenericViewSet):
    serializer_class = UserSavedEventsListSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'item'

    def get_queryset(self):
        return Event.saved_by.through.objects.filter(
            user=self.request.user
        )


class UserSignedUpEventsViewSet(
    RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    serializer_class = UserSavedEventsListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return ItemVariant.acquired_by.through.objects.filter(
            user=self.request.user
        )
