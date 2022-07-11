import rest_framework.serializers as serializers
from api.serializers.item import ItemDetailSerializer, ItemListSerializer
from api.models import Subscription


class SubscriptionListSerializer(ItemListSerializer):
    variants = serializers.SlugRelatedField(many=True, read_only=True,
                                            slug_field='id')

    class Meta(ItemDetailSerializer.Meta):
        model = Subscription
        fields = ItemListSerializer.Meta.fields + ['description',
                                                   'benefits', 'variants']


class SubscriptionDetailSerializer(ItemDetailSerializer):

    class Meta(ItemDetailSerializer.Meta):
        model = Subscription
        fields = ItemDetailSerializer.Meta.fields + ['description', 'benefits']
