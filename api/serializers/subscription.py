from api.serializers.item import ItemDetailSerializer, ItemListSerializer, \
    VariantSerializer
from api.models import Subscription


class SubscriptionVariantSerializer(VariantSerializer):
    class Meta:
        model = VariantSerializer.Meta.model
        fields = VariantSerializer.Meta.fields + ['benefits']


class SubscriptionListSerializer(ItemListSerializer):

    class Meta(ItemDetailSerializer.Meta):
        model = Subscription


class SubscriptionDetailSerializer(ItemDetailSerializer):
    variants = SubscriptionVariantSerializer(many=True)

    class Meta(ItemDetailSerializer.Meta):
        model = Subscription
