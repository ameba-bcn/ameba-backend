from rest_framework.permissions import AllowAny

from api.views import base
from api.serializers import LegalSerializer
from api.models import LegalDocument


class LegalViewSet(base.BaseReadOnlyViewSet):
    list_serializer = LegalSerializer
    detail_serializer = LegalSerializer
    model = LegalDocument
    permission_classes = (AllowAny, )
    queryset = LegalDocument.objects.filter(is_active=True).order_by('position')
