from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny

from api.serializers import CoverSerializer
from api.models import Cover


class CoversViewSet(ListModelMixin, GenericViewSet):
    serializer_class = CoverSerializer
    model = Cover
    permission_classes = (AllowAny, )
    queryset = Cover.objects.filter(is_active=True).order_by(
        'index', '-created'
    )
