import rest_framework.serializers as serializers
from api.serializers.item import ItemDetailSerializer, ItemListSerializer
from api.models import Subscription


class SubscriptionListSerializer(ItemListSerializer):

    class Meta(ItemDetailSerializer.Meta):
        model = Subscription
        fields = ItemDetailSerializer.Meta.fields + ['benefits']


class SubscriptionDetailSerializer(ItemDetailSerializer):

    class Meta(ItemDetailSerializer.Meta):
        model = Subscription
        fields = ItemDetailSerializer.Meta.fields + ['benefits']
