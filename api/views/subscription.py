from api.serializers import (
    SubscriptionListSerializer, SubscriptionDetailSerializer
)
from api.models import Subscription
from api.views.base import BaseReadOnlyViewSet


class SubscriptionViewSet(BaseReadOnlyViewSet):
    list_serializer = SubscriptionListSerializer
    detail_serializer = SubscriptionDetailSerializer
    model = Subscription
    queryset = Subscription.objects.filter(is_active=True)
