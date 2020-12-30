from api.serializers import ItemListSerializer, ItemDetailSerializer
from api.models import Item
from api.views.base import BaseReadOnlyViewSet


class ItemViewSet(BaseReadOnlyViewSet):
    list_serializer = ItemListSerializer
    detail_serializer = ItemDetailSerializer
    model = Item
