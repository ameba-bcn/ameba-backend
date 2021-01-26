from api.serializers.item import (BaseItemDetailSerializer,
                                  BaseItemListSerializer)
from api.models import Subscription


class SubscriptionDetailSerializer(BaseItemDetailSerializer):

    class Meta(BaseItemDetailSerializer.Meta):
        model = Subscription
        fields = BaseItemDetailSerializer.Meta.fields + ['benefits']


class SubscriptionListSerializer(BaseItemListSerializer):

    class Meta(BaseItemDetailSerializer.Meta):
        model = Subscription
