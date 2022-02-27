from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from api.serializers import ManifestSerializer
from api.models import Manifest


@swagger_auto_schema(method='get', query_serializer=ManifestSerializer)
@api_view(['GET'])
def manifest(request):
    about_obj = Manifest.objects.filter(is_active=True).order_by('-created').first()
    serializer = ManifestSerializer(instance=about_obj)
    return Response(serializer.data)
