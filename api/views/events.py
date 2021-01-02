from api.serializers import ItemListSerializer, ItemDetailSerializer
from api.models import Item
from api.views.base import BaseReadOnlyViewSet


class EventViewSet(BaseReadOnlyViewSet):
    list_serializer = ItemListSerializer
    detail_serializer = ItemDetailSerializer
    model = Item

    def get_queryset(self):
        return Item.objects.filter(is_expired=False, type='event')
