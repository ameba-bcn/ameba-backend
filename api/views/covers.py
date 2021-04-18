from api.serializers import CoverSerializer
from api.models import Cover
from api.views.base import BaseReadOnlyViewSet


class CoversViewSet(BaseReadOnlyViewSet):
    list_serializer = CoverSerializer
    detail_serializer = CoverSerializer
    model = Cover
    queryset = Cover.objects.filter(is_active=True).order_by(
        'index', '-created'
    )
