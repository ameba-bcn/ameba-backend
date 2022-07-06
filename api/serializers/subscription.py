from api.serializers.item import ItemDetailSerializer, ItemListSerializer, \
    VariantSerializer
from api.models import Subscription


class SubscriptionListSerializer(ItemListSerializer):

    class Meta(ItemDetailSerializer.Meta):
        model = Subscription
        fields = ItemListSerializer.Meta.fields + ['description', 'benefits']


class SubscriptionDetailSerializer(ItemDetailSerializer):

    class Meta(ItemDetailSerializer.Meta):
        model = Subscription
        fields = ItemDetailSerializer.Meta.fields + ['description', 'benefits']
