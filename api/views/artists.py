from api.serializers import ArtistSerializer, ArtistListSerializer
from api.models import Artist
from api.views.base import BaseReadOnlyViewSet


class ArtistViewSet(BaseReadOnlyViewSet):
    list_serializer = ArtistListSerializer
    detail_serializer = ArtistSerializer
    model = Artist
    queryset = Artist.objects.all().order_by('-created').prefetch_related(
        'tags', 'images'
    )
