from api.serializers import EventListSerializer, EventDetailSerializer
from api.models import Event
from api.views.base import BaseReadOnlyViewSet


class EventViewSet(BaseReadOnlyViewSet):
    list_serializer = EventListSerializer
    detail_serializer = EventDetailSerializer
    model = Event
    queryset = Event.objects.filter(is_active=True)
