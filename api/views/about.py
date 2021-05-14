from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from api.serializers import AboutSerializer
from api.models import About


@swagger_auto_schema(method='get', request_body=AboutSerializer)
@api_view(['GET'])
def activate(request):
    about = About.objects.filter(is_active=True).order_by('-created').first()
    serializer = AboutSerializer(instance=about)
    return Response(serializer.data)
