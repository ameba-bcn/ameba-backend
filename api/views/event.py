from api.serializers import EventListSerializer, EventDetailSerializer
from api.models import Event
from api.views.base import BaseReadOnlyViewSet


class ArticleViewSet(BaseReadOnlyViewSet):
    list_serializer = EventListSerializer
    detail_serializer = EventDetailSerializer
    model = Event
